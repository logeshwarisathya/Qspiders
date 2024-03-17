from django.urls import path
from myapp import views
from myapp import addcart
from myapp import register



urlpatterns= [
    path('',views.home,name="home"),
    path('register',register.register,name="register"),
    path('login',views.login_page,name="login"),
    path('collections',views.collections,name="collections"),
    path('collections/<str:name>',views.collectionsview,name="collections"),
    path('collections/<str:cname>/<str:pname>',views.product_details,name="product_details"),
    path('addtocart',addcart.add_to_cart,name="addtocart"),
    path('cart',views.cart_page,name="cart"),
    path('remove_cart/<str:cid>',views.remove_cart,name="remove_cart"),
    path('fav',views.fav_page,name="fav"),
    path('remove_fav/<str:fid>',views.remove_fav,name="remove_fav"),
    path('favviewpage',views.favviewpage,name="favviewpage"),
    path('signout',views.signout,name='signout'),
    path('checkout',views.checkout,name='checkout'),
    path('placeorder',views.placeorder,name='placeorder'),
    
    path('proceed-to-pay',views.razorpaycheck),

]