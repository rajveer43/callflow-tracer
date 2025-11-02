"""
Real-World Integration Example

This demonstrates how to integrate callflow-tracer's new features
into a real application for continuous quality monitoring.

Scenario: E-commerce API with quality monitoring
"""

import time
import random
from datetime import datetime
from typing import List, Dict, Optional


# ============================================================================
# Simulated E-commerce Application
# ============================================================================

class Product:
    """Product model."""
    def __init__(self, id: int, name: str, price: float, stock: int):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock


class Order:
    """Order model."""
    def __init__(self, id: int, customer_id: int, items: List[Dict], total: float):
        self.id = id
        self.customer_id = customer_id
        self.items = items
        self.total = total
        self.status = "pending"


class EcommerceAPI:
    """
    Simulated e-commerce API with various quality issues.
    
    This class demonstrates:
    - Functions with different complexity levels
    - Performance degradation patterns
    - Memory management issues
    - Code that needs refactoring
    """
    
    def __init__(self):
        self.products = self._initialize_products()
        self.orders = []
        self.cache = {}
        self.request_count = 0
    
    def _initialize_products(self) -> List[Product]:
        """Initialize product catalog."""
        return [
            Product(1, "Laptop", 999.99, 50),
            Product(2, "Mouse", 29.99, 200),
            Product(3, "Keyboard", 79.99, 150),
            Product(4, "Monitor", 299.99, 75),
            Product(5, "Headphones", 149.99, 100),
        ]
    
    # ========================================================================
    # EXAMPLE 1: Simple, well-structured function (LOW COMPLEXITY)
    # ========================================================================
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """
        Get product by ID.
        
        Complexity: LOW (1-2)
        Maintainability: HIGH
        """
        for product in self.products:
            if product.id == product_id:
                return product
        return None
    
    # ========================================================================
    # EXAMPLE 2: Moderate complexity (ACCEPTABLE)
    # ========================================================================
    
    def search_products(self, query: str, min_price: float = 0, 
                       max_price: float = float('inf')) -> List[Product]:
        """
        Search products with filters.
        
        Complexity: MODERATE (5-7)
        Maintainability: GOOD
        """
        results = []
        
        for product in self.products:
            # Name match
            if query.lower() in product.name.lower():
                # Price filter
                if min_price <= product.price <= max_price:
                    # Stock check
                    if product.stock > 0:
                        results.append(product)
        
        return results
    
    # ========================================================================
    # EXAMPLE 3: High complexity - NEEDS REFACTORING
    # ========================================================================
    
    def process_order(self, customer_id: int, items: List[Dict], 
                     payment_method: str, shipping_method: str,
                     promo_code: Optional[str] = None,
                     gift_wrap: bool = False,
                     express_shipping: bool = False) -> Dict:
        """
        Process an order with multiple options.
        
        WARNING: HIGH COMPLEXITY (15+)
        This function should be refactored into smaller functions!
        
        Issues:
        - Too many parameters
        - Deep nesting
        - Multiple responsibilities
        - Hard to test
        - Poor maintainability
        """
        self.request_count += 1
        
        # Validate items
        total = 0
        validated_items = []
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            product = self.get_product(product_id)
            
            if product:
                if product.stock >= quantity:
                    if quantity > 0:
                        item_total = product.price * quantity
                        
                        # Apply bulk discount
                        if quantity >= 10:
                            item_total *= 0.9
                        elif quantity >= 5:
                            item_total *= 0.95
                        
                        validated_items.append({
                            'product': product,
                            'quantity': quantity,
                            'subtotal': item_total
                        })
                        total += item_total
                    else:
                        return {'error': 'Invalid quantity'}
                else:
                    return {'error': f'Insufficient stock for {product.name}'}
            else:
                return {'error': f'Product {product_id} not found'}
        
        # Apply promo code
        if promo_code:
            if promo_code == 'SAVE10':
                total *= 0.9
            elif promo_code == 'SAVE20':
                total *= 0.8
            elif promo_code == 'SAVE5':
                total *= 0.95
        
        # Calculate shipping
        shipping_cost = 0
        if shipping_method == 'standard':
            shipping_cost = 5.99
            if express_shipping:
                shipping_cost = 15.99
        elif shipping_method == 'express':
            shipping_cost = 15.99
        elif shipping_method == 'overnight':
            shipping_cost = 29.99
        
        # Free shipping for orders over $100
        if total > 100:
            shipping_cost = 0
        
        total += shipping_cost
        
        # Gift wrap
        if gift_wrap:
            total += 4.99
        
        # Process payment
        if payment_method == 'credit_card':
            # Simulate payment processing
            time.sleep(0.01)
            payment_status = 'success'
        elif payment_method == 'paypal':
            time.sleep(0.015)
            payment_status = 'success'
        elif payment_method == 'bank_transfer':
            time.sleep(0.02)
            payment_status = 'pending'
        else:
            return {'error': 'Invalid payment method'}
        
        # Create order
        order = Order(
            id=len(self.orders) + 1,
            customer_id=customer_id,
            items=validated_items,
            total=total
        )
        
        if payment_status == 'success':
            order.status = 'confirmed'
            
            # Update stock
            for item in validated_items:
                item['product'].stock -= item['quantity']
        
        self.orders.append(order)
        
        return {
            'order_id': order.id,
            'status': order.status,
            'total': total,
            'shipping_cost': shipping_cost
        }
    
    # ========================================================================
    # EXAMPLE 4: Performance degradation pattern
    # ========================================================================
    
    def get_order_history(self, customer_id: int) -> List[Order]:
        """
        Get customer order history.
        
        WARNING: Performance degrades as orders grow!
        This demonstrates a function that gets slower over time.
        """
        # Simulate increasing database query time
        time.sleep(0.001 * len(self.orders))
        
        # Inefficient filtering (should use indexing)
        customer_orders = []
        for order in self.orders:
            if order.customer_id == customer_id:
                customer_orders.append(order)
        
        # Inefficient sorting
        for i in range(len(customer_orders)):
            for j in range(i + 1, len(customer_orders)):
                if customer_orders[i].id > customer_orders[j].id:
                    customer_orders[i], customer_orders[j] = customer_orders[j], customer_orders[i]
        
        return customer_orders
    
    # ========================================================================
    # EXAMPLE 5: Memory leak pattern
    # ========================================================================
    
    def cache_product_recommendations(self, customer_id: int) -> List[Product]:
        """
        Get product recommendations with caching.
        
        WARNING: Memory leak - cache grows indefinitely!
        """
        cache_key = f"recommendations_{customer_id}"
        
        # Cache never expires - memory leak!
        if cache_key not in self.cache:
            # Simulate recommendation algorithm
            recommendations = random.sample(self.products, min(3, len(self.products)))
            self.cache[cache_key] = recommendations
        
        return self.cache[cache_key]
    
    # ========================================================================
    # EXAMPLE 6: Well-refactored version
    # ========================================================================
    
    def process_order_refactored(self, customer_id: int, items: List[Dict],
                                 payment_method: str, shipping_method: str,
                                 **options) -> Dict:
        """
        Refactored version with better structure.
        
        Complexity: LOW (3-4)
        Maintainability: HIGH
        
        Improvements:
        - Single responsibility
        - Clear separation of concerns
        - Easy to test
        - Better error handling
        """
        # Validate and calculate
        validation_result = self._validate_order_items(items)
        if 'error' in validation_result:
            return validation_result
        
        # Calculate totals
        subtotal = validation_result['subtotal']
        total = self._calculate_total(subtotal, options)
        
        # Process payment
        payment_result = self._process_payment(payment_method, total)
        if 'error' in payment_result:
            return payment_result
        
        # Create and save order
        order = self._create_order(customer_id, validation_result['items'], total)
        
        return {
            'order_id': order.id,
            'status': order.status,
            'total': total
        }
    
    def _validate_order_items(self, items: List[Dict]) -> Dict:
        """Validate order items and calculate subtotal."""
        validated_items = []
        subtotal = 0
        
        for item in items:
            product = self.get_product(item.get('product_id'))
            quantity = item.get('quantity', 1)
            
            if not product:
                return {'error': f"Product {item.get('product_id')} not found"}
            
            if product.stock < quantity:
                return {'error': f"Insufficient stock for {product.name}"}
            
            item_total = product.price * quantity
            validated_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': item_total
            })
            subtotal += item_total
        
        return {'items': validated_items, 'subtotal': subtotal}
    
    def _calculate_total(self, subtotal: float, options: Dict) -> float:
        """Calculate final total with discounts and fees."""
        total = subtotal
        
        # Apply promo code
        if promo_code := options.get('promo_code'):
            total *= self._get_promo_discount(promo_code)
        
        # Add shipping
        total += self._calculate_shipping(subtotal, options.get('shipping_method'))
        
        # Add extras
        if options.get('gift_wrap'):
            total += 4.99
        
        return total
    
    def _get_promo_discount(self, promo_code: str) -> float:
        """Get discount multiplier for promo code."""
        discounts = {
            'SAVE10': 0.9,
            'SAVE20': 0.8,
            'SAVE5': 0.95
        }
        return discounts.get(promo_code, 1.0)
    
    def _calculate_shipping(self, subtotal: float, method: str) -> float:
        """Calculate shipping cost."""
        if subtotal > 100:
            return 0.0
        
        shipping_costs = {
            'standard': 5.99,
            'express': 15.99,
            'overnight': 29.99
        }
        return shipping_costs.get(method, 5.99)
    
    def _process_payment(self, method: str, amount: float) -> Dict:
        """Process payment."""
        # Simulate payment processing
        time.sleep(0.01)
        return {'status': 'success'}
    
    def _create_order(self, customer_id: int, items: List[Dict], total: float) -> Order:
        """Create and save order."""
        order = Order(
            id=len(self.orders) + 1,
            customer_id=customer_id,
            items=items,
            total=total
        )
        order.status = 'confirmed'
        self.orders.append(order)
        return order


# ============================================================================
# Quality Monitoring Integration
# ============================================================================

def monitor_api_quality():
    """
    Demonstrate continuous quality monitoring.
    
    This shows how to integrate quality analysis into your application.
    """
    print("=" * 70)
    print("REAL-WORLD INTEGRATION: E-commerce API Quality Monitoring")
    print("=" * 70)
    
    try:
        from callflow_tracer import (
            ComplexityAnalyzer,
            MaintainabilityAnalyzer,
            TechnicalDebtAnalyzer
        )
        
        # Analyze this file
        print("\n📊 Analyzing API code quality...")
        
        comp_analyzer = ComplexityAnalyzer()
        maint_analyzer = MaintainabilityAnalyzer()
        
        complexity_metrics = comp_analyzer.analyze_file(__file__)
        maintainability_metrics = maint_analyzer.analyze_file(__file__)
        
        # Find the problematic function
        process_order_metric = next(
            (m for m in complexity_metrics if m.function_name == 'process_order'),
            None
        )
        
        process_order_refactored_metric = next(
            (m for m in complexity_metrics if m.function_name == 'process_order_refactored'),
            None
        )
        
        if process_order_metric and process_order_refactored_metric:
            print("\n🔍 Comparison: Original vs Refactored")
            print("-" * 70)
            
            print(f"\nprocess_order (ORIGINAL):")
            print(f"  Cyclomatic Complexity: {process_order_metric.cyclomatic_complexity}")
            print(f"  Rating: {process_order_metric.complexity_rating}")
            print(f"  Lines of Code: {process_order_metric.lines_of_code}")
            print(f"  Nesting Depth: {process_order_metric.nesting_depth}")
            
            print(f"\nprocess_order_refactored (IMPROVED):")
            print(f"  Cyclomatic Complexity: {process_order_refactored_metric.cyclomatic_complexity}")
            print(f"  Rating: {process_order_refactored_metric.complexity_rating}")
            print(f"  Lines of Code: {process_order_refactored_metric.lines_of_code}")
            print(f"  Nesting Depth: {process_order_refactored_metric.nesting_depth}")
            
            improvement = ((process_order_metric.cyclomatic_complexity - 
                          process_order_refactored_metric.cyclomatic_complexity) /
                          process_order_metric.cyclomatic_complexity * 100)
            
            print(f"\n✅ Complexity reduced by {improvement:.1f}% through refactoring!")
        
        # Technical debt analysis
        debt_analyzer = TechnicalDebtAnalyzer()
        debt_indicators = debt_analyzer.analyze_from_metrics(
            complexity_metrics,
            maintainability_metrics
        )
        
        if debt_indicators:
            print(f"\n⚠️  Technical Debt Report")
            print("-" * 70)
            
            high_debt = [d for d in debt_indicators if d.severity in ['Critical', 'High']]
            
            if high_debt:
                print(f"\nFound {len(high_debt)} high-priority issues:\n")
                
                for debt in high_debt[:3]:
                    print(f"• {debt.function_name}")
                    print(f"  Severity: {debt.severity}")
                    print(f"  Debt Score: {debt.debt_score:.1f}/100")
                    print(f"  Estimated Fix Time: {debt.estimated_hours:.1f} hours")
                    print(f"  Issues: {', '.join(debt.issues[:2])}")
                    print()
        
        print("\n💡 Recommendations:")
        print("-" * 70)
        print("1. Refactor high-complexity functions (complexity > 10)")
        print("2. Add caching with expiration to prevent memory leaks")
        print("3. Optimize database queries for better scalability")
        print("4. Add comprehensive unit tests for complex functions")
        print("5. Set up continuous quality monitoring in CI/CD")
        
    except ImportError:
        print("\n⚠️  callflow-tracer not installed")
        print("Run: pip install -e .")


def simulate_performance_monitoring():
    """Demonstrate performance monitoring over time."""
    print("\n" + "=" * 70)
    print("PERFORMANCE MONITORING SIMULATION")
    print("=" * 70)
    
    api = EcommerceAPI()
    
    print("\nSimulating API usage over time...")
    print("(Watch how performance degrades as data grows)\n")
    
    # Simulate orders over time
    for i in range(1, 11):
        # Create some orders
        for _ in range(10):
            api.process_order(
                customer_id=random.randint(1, 100),
                items=[{'product_id': random.randint(1, 5), 'quantity': random.randint(1, 3)}],
                payment_method='credit_card',
                shipping_method='standard'
            )
        
        # Measure get_order_history performance
        start = time.time()
        api.get_order_history(customer_id=1)
        elapsed = time.time() - start
        
        print(f"Iteration {i:2d}: {len(api.orders):3d} orders, query time: {elapsed:.6f}s")
    
    print(f"\n⚠️  Performance degraded as data grew!")
    print(f"   Cache size: {len(api.cache)} entries (memory leak)")
    print(f"   Total requests: {api.request_count}")
    
    print("\n💡 Use 'callflow predict' to forecast such issues before they happen!")


def main():
    """Run the integration demo."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 12 + "REAL-WORLD INTEGRATION EXAMPLE" + " " * 26 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Run demos
    monitor_api_quality()
    simulate_performance_monitoring()
    
    # Summary
    print("\n" + "=" * 70)
    print("INTEGRATION GUIDE")
    print("=" * 70)
    
    print("\n1️⃣  Add to CI/CD Pipeline:")
    print("   callflow quality ./src --format json -o quality.json")
    print("   python scripts/check_quality_gates.py")
    
    print("\n2️⃣  Monitor Performance:")
    print("   callflow trace app.py --format json -o trace_$(date +%Y%m%d).json")
    print("   callflow predict trace_history.json")
    
    print("\n3️⃣  Track Code Churn:")
    print("   callflow churn . --days 30 -o churn_report.html")
    
    print("\n4️⃣  Set Quality Gates:")
    print("   - Max complexity: 10")
    print("   - Min maintainability: 60")
    print("   - Max technical debt: 100")
    
    print("\n✅ Integration Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
