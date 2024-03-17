from django.http import JsonResponse
from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages
from myapp.form import CustomUserForm
from django.contrib.auth import authenticate,login,logout
import json
from django.contrib.auth.decorators import login_required
import random
# Create your views here.

def home(request):
    products=Product.objects.filter(trending=1)
    return render(request,"shop/index.html",{"products":products})

def cart_page(request):
  if request.user.is_authenticated:
    cart=Cart.objects.filter(user=request.user)
    return render(request,"shop/cart.html",{"cart":cart})
  else:
    return redirect("/")
  
def remove_cart(request,cid):
  cartitem=Cart.objects.get(id=cid)
  cartitem.delete()
  return redirect("/cart") 

def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("/favviewpage")  
 
def favviewpage(request):
  if request.user.is_authenticated:
    fav=Favourite.objects.filter(user=request.user)
    return render(request,"shop/fav.html",{"fav":fav})
  else:
    return redirect("/")

def fav_page(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
        if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
        else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
      
     
    else:
      return JsonResponse({'status':'Login to Add Favourite'}, status=200)
   else:
     return JsonResponse({'status':'Invalid Access'}, status=200)
   



def add_to_cart(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_qty=data['product_qty']
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
        if Cart.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Cart'}, status=200)
        else:
          if product_status.quantity>=product_qty:
            Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
            return JsonResponse({'status':'Product Added to Cart'}, status=200)
          else:
            return JsonResponse({'status':'Product Stock Not Available'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Cart'}, status=200)
   else:
     return JsonResponse({'status':'Invalid Access'}, status=200)
   


@login_required(login_url="/login/")
def placeorder(request):
  if request.method == 'POST':
    neworder=Order()
    neworder.user=request.user
    neworder.fname=request.POST.get('fname')
    neworder.lname=request.POST.get('lname')
    neworder.email=request.POST.get('email')
    neworder.phone=request.POST.get('phone')
    neworder.address=request.POST.get('address')
    neworder.city=request.POST.get('city')
    neworder.state=request.POST.get('state')
    neworder.country=request.POST.get('country')
    neworder.pincode=request.POST.get('pincode')

    neworder.payment_mode=request.POST.get('payment_mode')

    cart=Cart.objects.filter(user=request.user)
    cart_total_price = 0
    for item in cart:
      cart_total_price = cart_total_price + item.product.selling_price * item.product_qty

    neworder.total_price = cart_total_price
    trackno = 'sharma'+str(random.randint(1111111,9999999))
    while Order.objects.filter(tracking_no=trackno) is None:
      trackno = 'sharma'+str(random.randint(1111111,9999999))

    neworder.tracking_no= trackno
    neworder.save()

    neworderitems = Cart.objects.filter(user=request.user)
    for item in neworderitems:
      OrderItem.objects.create(
        order=neworder,
        product=item.product,
        price=item.product.selling_price,
        quantity=item.product_qty
      )

      # To decrease the product quantity from available stock
      orderproduct = Product.objects.filter(id=item.product_id).first()
      orderproduct.quantity=orderproduct.quantity - item.product_qty
      orderproduct.save()

    # To clear user's Cart
    Cart.objects.filter(user=request.user).delete()

    messages.success(request,"Your order has been placed successfully")


  return redirect('/')

def checkout(request):
  rawcart=Cart.objects.filter(user=request.user)
  for item in rawcart:
    if item.product_qty > item.product.quantity :
      Cart.objects.filter(user=request.user).delete()

      # Cart.objects.delete(id=item.id)

  cartitems = Cart.objects.filter(user=request.user)
  total_price = 0
  for item in cartitems:
    total_price = total_price + item.product.selling_price * item.product_qty    

  context={'cartitems':cartitems,'total_price':total_price}
  return render(request,"shop/checkout.html",context)

def login_page(request):
  if request.user.is_authenticated:
    return redirect("/")
  else:
    if request.method=='POST':
       name=request.POST.get('username')
       pwd=request.POST.get('password')
       user=authenticate(request,username=name,password=pwd)
       if user is not None:
          login(request,user)
          messages.success(request,"Logged in Successfully")
          return redirect("/")
       else:
          messages.error(request,"Invalid User Name or Password")
          return redirect("/login")   
    return render(request,"shop/login.html")


@login_required(login_url="/login/")
def signout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("/login")

def register(request):
    form=CustomUserForm()
    if request.method=='POST':
       form=CustomUserForm(request.POST)
       if form.is_valid():
          form.save()
          messages.success(request,"Registration Success You can Login Now..!")
          return redirect('/login')
    return render(request,"shop/register.html",{'form':form})

def collections(request):
    catagory=Catagory.objects.filter(status=0)
    return render(request,"shop/collections.html",{"catagory":catagory})

def collectionsview(request,name):
  if(Catagory.objects.filter(name=name,status=0)):
      products=Product.objects.filter(category__name=name)
      return render(request,"shop/products/index.html",{"products":products,"category_name":name})
  else:
    messages.warning(request,"No Such Catagory Found")
    return redirect('collections/')
  
def product_details(request,cname,pname):
  if(Catagory.objects.filter(name=cname,status=0)):
     if(Product.objects.filter(name=pname,status=0)):
        products=Product.objects.filter(name=pname,status=0).first()
        return render(request,"shop/products/product_details.html",{"products":products})
     else:
        messages.warning(request,"No Such Product Found")
        return redirect('collections')


  else:
    messages.warning(request,"No Such Catagory Found")
    return redirect('collections')

   
@login_required(login_url="/login/")
def razorpaycheck(request):
    cart =Cart.objects.filter(user=request.user)
    total_price =0
    for item in cart:
      total_price = total_price + item.product.selling_price*item.product_qty

    return JsonResponse({
      'total_price': total_price
    })

