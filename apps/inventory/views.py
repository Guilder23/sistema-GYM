from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Sale, ProductCategory, SaleItem
from apps.clients.models import Client
from apps.core.models import UserProfile
from apps.core.permissions import role_required


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def product_list(request):
    search_query = request.GET.get('q', '')
    products = Product.objects.all().order_by('name')
    if search_query:
        products = products.filter(name__icontains=search_query)
    context = {'products': products, 'search_query': search_query}
    return render(request, 'inventory/product_list.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def product_create(request):
    categories = ProductCategory.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price', 0)
        stock = request.POST.get('stock', 0)
        min_stock = request.POST.get('min_stock', 5)
        category_id = request.POST.get('category_id')
        barcode = request.POST.get('barcode', '')
        
        category = None
        if category_id:
            category = ProductCategory.objects.get(id=category_id)
            
        Product.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            min_stock=min_stock,
            category=category,
            barcode=barcode or None
        )
        messages.success(request, 'Producto creado correctamente.')
        return redirect('product_list')
    
    return render(request, 'inventory/product_form.html', {'categories': categories})


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = ProductCategory.objects.all()
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description', '')
        product.price = request.POST.get('price', 0)
        product.stock = request.POST.get('stock', 0)
        product.min_stock = request.POST.get('min_stock', 5)
        category_id = request.POST.get('category_id')
        product.barcode = request.POST.get('barcode', '') or None
        
        if category_id:
            product.category = ProductCategory.objects.get(id=category_id)
        else:
            product.category = None
            
        product.save()
        messages.success(request, 'Producto actualizado correctamente.')
        return redirect('product_list')
    
    return render(request, 'inventory/product_form.html', {'product': product, 'categories': categories})


# Lógica del Carrito de Compras
@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def cart_add(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)
    
    if product.stock <= 0:
        messages.error(request, f'El producto {product.name} está agotado.')
        return redirect('product_list')
        
    p_id = str(product_id)
    if p_id in cart:
        cart[p_id]['quantity'] += 1
    else:
        cart[p_id] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1
        }
    
    request.session['cart'] = cart
    messages.success(request, f'{product.name} añadido al carrito.')
    return redirect('product_list')


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def cart_detail(request):
    cart = request.session.get('cart', {})
    clients = Client.objects.filter(is_active=True).order_by('first_name')
    total = 0
    cart_items = []
    
    for p_id, item in cart.items():
        subtotal = float(item['price']) * item['quantity']
        total += subtotal
        cart_items.append({
            'id': p_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'subtotal': subtotal
        })
        
    context = {
        'cart_items': cart_items,
        'total': total,
        'clients': clients
    }
    return render(request, 'inventory/cart_detail.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    p_id = str(product_id)
    if p_id in cart:
        del cart[p_id]
        request.session['cart'] = cart
        messages.success(request, 'Producto eliminado del carrito.')
    return redirect('cart_detail')


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def cart_clear(request):
    request.session['cart'] = {}
    return redirect('product_list')


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def cart_checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('product_list')
        
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        notes = request.POST.get('notes', '')
        
        client = None
        if client_id:
            client = get_object_or_404(Client, id=client_id)
            
        total = sum(float(item['price']) * item['quantity'] for item in cart.values())
        
        sale = Sale.objects.create(
            client=client,
            total=total,
            notes=notes
        )
        
        for p_id, item in cart.items():
            product = get_object_or_404(Product, id=p_id)
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=item['quantity'],
                price=item['price']
            )
            # Descontar stock
            product.stock -= item['quantity']
            product.save()
            
        request.session['cart'] = {}
        messages.success(request, 'Venta realizada con éxito.')
        return redirect('sale_list')
        
    return redirect('cart_detail')


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def sale_list(request):
    sales = Sale.objects.all().order_by('-date')
    context = {'sales': sales}
    return render(request, 'inventory/sale_list.html', context)
