import iyzipay
from typing import Dict, Optional
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class IyzicoService:
    def __init__(self):
        self.api_key = os.environ.get('IYZICO_API_KEY')
        self.secret_key = os.environ.get('IYZICO_SECRET_KEY')
        self.base_url = os.environ.get('IYZICO_BASE_URL')
        
        # İyzico options
        self.options = {
            'api_key': self.api_key,
            'secret_key': self.secret_key,
            'base_url': self.base_url
        }
    
    def create_checkout_form(self, user_data: dict, package_type: str) -> Dict:
        """Create İyzico checkout form for subscription"""
        try:
            # Package pricing
            pricing = {
                'standard': '300.0',
                'premium': '1000.0'
            }
            
            price = pricing.get(package_type, '300.0')
            
            # Checkout form request
            request = {
                'locale': iyzipay.Locale.TR,
                'conversationId': f"dermavision_{user_data['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'price': price,
                'paidPrice': price,
                'currency': iyzipay.Currency.TRY,
                'basketId': f"B{user_data['id']}",
                'paymentGroup': iyzipay.PaymentGroup.SUBSCRIPTION,
                'callbackUrl': f"{os.environ.get('FRONTEND_URL', 'https://dermavision.preview.emergentagent.com')}/payment/callback",
                'enabledInstallments': [1],
                'buyer': {
                    'id': user_data['id'],
                    'name': user_data['full_name'].split()[0] if user_data['full_name'] else 'User',
                    'surname': user_data['full_name'].split()[-1] if len(user_data['full_name'].split()) > 1 else 'Surname',
                    'gsmNumber': user_data.get('phone', '+905350000000'),
                    'email': user_data['email'],
                    'identityNumber': user_data.get('identity_number', '74300864791'),
                    'lastLoginDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'registrationDate': user_data.get('created_at', datetime.now()).strftime('%Y-%m-%d %H:%M:%S'),
                    'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
                    'ip': '85.34.78.112',
                    'city': 'Istanbul',
                    'country': 'Turkey',
                    'zipCode': '34732'
                },
                'shippingAddress': {
                    'contactName': user_data['full_name'],
                    'city': 'Istanbul',
                    'country': 'Turkey',
                    'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
                    'zipCode': '34732'
                },
                'billingAddress': {
                    'contactName': user_data['full_name'],
                    'city': 'Istanbul',
                    'country': 'Turkey',
                    'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
                    'zipCode': '34732'
                },
                'basketItems': [
                    {
                        'id': f"dermavision_{package_type}",
                        'name': f'DermaVision AI {package_type.title()} Paket',
                        'category1': 'Health',
                        'category2': 'AI Analysis',
                        'itemType': iyzipay.BasketItemType.VIRTUAL,
                        'price': price
                    }
                ]
            }
            
            checkout_form_initialize = iyzipay.CheckoutFormInitialize()
            checkout_form_initialize_response = checkout_form_initialize.create(request, self.options)
            
            if checkout_form_initialize_response.status == 'success':
                return {
                    'success': True,
                    'checkout_form_content': checkout_form_initialize_response.checkout_form_content,
                    'payment_page_url': checkout_form_initialize_response.payment_page_url,
                    'token': checkout_form_initialize_response.token,
                    'conversation_id': request['conversationId']
                }
            else:
                logger.error(f"İyzico checkout form error: {checkout_form_initialize_response.error_message}")
                return {
                    'success': False,
                    'error': checkout_form_initialize_response.error_message
                }
                
        except Exception as e:
            logger.error(f"İyzico service error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def retrieve_checkout_form_result(self, token: str) -> Dict:
        """Retrieve payment result using token"""
        try:
            request = {
                'locale': iyzipay.Locale.TR,
                'token': token
            }
            
            checkout_form = iyzipay.CheckoutForm()
            checkout_result = checkout_form.retrieve(request, self.options)
            
            if checkout_result.status == 'success':
                return {
                    'success': True,
                    'payment_id': checkout_result.payment_id,
                    'payment_status': checkout_result.payment_status,
                    'fraud_status': checkout_result.fraud_status,
                    'merchant_commission_rate': checkout_result.merchant_commission_rate,
                    'merchant_commission_rate_amount': checkout_result.merchant_commission_rate_amount,
                    'iyzi_commission_rate_amount': checkout_result.iyzi_commission_rate_amount,
                    'iyzi_commission_fee': checkout_result.iyzi_commission_fee,
                    'card_type': checkout_result.card_type,
                    'card_association': checkout_result.card_association,
                    'card_family': checkout_result.card_family,
                    'bin_number': checkout_result.bin_number,
                    'last_four_digits': checkout_result.last_four_digits,
                    'basket_id': checkout_result.basket_id,
                    'currency': checkout_result.currency,
                    'paid_price': checkout_result.paid_price,
                    'price': checkout_result.price
                }
            else:
                logger.error(f"İyzico checkout result error: {checkout_result.error_message}")
                return {
                    'success': False,
                    'error': checkout_result.error_message
                }
                
        except Exception as e:
            logger.error(f"İyzico retrieve error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_refund(self, payment_id: str, amount: str, reason: str = "Customer request") -> Dict:
        """Create refund for a payment"""
        try:
            request = {
                'locale': iyzipay.Locale.TR,
                'conversationId': f"refund_{payment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'paymentTransactionId': payment_id,
                'price': amount,
                'ip': '85.34.78.112',
                'reason': reason
            }
            
            refund = iyzipay.Refund()
            refund_response = refund.create(request, self.options)
            
            if refund_response.status == 'success':
                return {
                    'success': True,
                    'refund_id': refund_response.payment_id,
                    'status': refund_response.status
                }
            else:
                logger.error(f"İyzico refund error: {refund_response.error_message}")
                return {
                    'success': False,
                    'error': refund_response.error_message
                }
                
        except Exception as e:
            logger.error(f"İyzico refund error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
iyzico_service = IyzicoService()
