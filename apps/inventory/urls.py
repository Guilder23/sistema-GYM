from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('nuevo/', views.product_create, name='product_create'),
    path('editar/<int:product_id>/', views.product_edit, name='product_edit'),
    path('ajustar-stock/<int:product_id>/', views.product_stock_adjust, name='product_stock_adjust'),
    path('ventas/', views.sale_list, name='sale_list'),
    path('ventas/<int:sale_id>/', views.sale_detail, name='sale_detail'),
    path('mis-compras/', views.my_purchases, name='my_purchases'),
    # Carrito
    path('carrito/', views.cart_detail, name='cart_detail'),
    path('carrito/añadir/<int:product_id>/', views.cart_add, name='cart_add'),
    path('carrito/eliminar/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('carrito/limpiar/', views.cart_clear, name='cart_clear'),
    path('carrito/checkout/', views.cart_checkout, name='cart_checkout'),
]
