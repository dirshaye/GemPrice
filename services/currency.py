import httpx
import os
from typing import Dict, Optional
from datetime import datetime, timedelta


class CurrencyExchangeService:
    """
    Service for handling currency exchange rates and conversions
    """
    
    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        
        # Fallback exchange rates (approximate)
        self.fallback_rates = {
            "USD": 1.0,
            "EUR": 0.85,
            "GBP": 0.73,
            "JPY": 110.0,
            "CAD": 1.25,
            "AUD": 1.35,
            "CHF": 0.92,
            "CNY": 6.45,
            "INR": 74.0,
            "KRW": 1180.0
        }
    
    async def get_exchange_rates(self, base_currency: str = "USD") -> Dict[str, float]:
        """
        Get current exchange rates for a base currency
        """
        try:
            # Check cache first
            cache_key = f"rates_{base_currency}"
            if (cache_key in self.cache and 
                cache_key in self.cache_expiry and
                datetime.now() < self.cache_expiry[cache_key]):
                print(f"💰 Using cached exchange rates for {base_currency}")
                return self.cache[cache_key]
            
            # Fetch from API
            print(f"💱 Fetching live exchange rates for {base_currency}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/{base_currency}")
                
                if response.status_code == 200:
                    data = response.json()
                    rates = data.get("rates", {})
                    
                    # Cache the results
                    self.cache[cache_key] = rates
                    self.cache_expiry[cache_key] = datetime.now() + self.cache_duration
                    
                    return rates
                else:
                    print(f"⚠️ Exchange API returned {response.status_code}, using fallback")
                    return self._get_fallback_rates(base_currency)
                    
        except Exception as e:
            print(f"❌ Error fetching exchange rates: {e}, using fallback")
            return self._get_fallback_rates(base_currency)
    
    def _get_fallback_rates(self, base_currency: str) -> Dict[str, float]:
        """
        Get fallback exchange rates when API is unavailable
        """
        if base_currency == "USD":
            return self.fallback_rates.copy()
        
        # Convert fallback rates to the requested base currency
        base_rate = self.fallback_rates.get(base_currency, 1.0)
        converted_rates = {}
        
        for currency, rate in self.fallback_rates.items():
            converted_rates[currency] = rate / base_rate
        
        return converted_rates
    
    async def convert_currency(self, 
                             amount: float, 
                             from_currency: str, 
                             to_currency: str = "USD") -> tuple[float, Dict[str, float]]:
        """
        Convert amount from one currency to another
        Returns: (converted_amount, exchange_rates_used)
        """
        try:
            if from_currency.upper() == to_currency.upper():
                return amount, {f"{from_currency}_to_{to_currency}": 1.0}
            
            # Get exchange rates
            rates = await self.get_exchange_rates(from_currency.upper())
            
            if to_currency.upper() in rates:
                conversion_rate = rates[to_currency.upper()]
                converted_amount = round(amount * conversion_rate, 2)
                
                print(f"💱 Converted {amount} {from_currency} to {converted_amount} {to_currency} (rate: {conversion_rate})")
                
                return converted_amount, {
                    f"{from_currency}_to_{to_currency}": conversion_rate,
                    "source": "live_api" if f"rates_{from_currency}" in self.cache else "fallback"
                }
            else:
                print(f"⚠️ Currency {to_currency} not supported, returning original amount")
                return amount, {"error": f"Currency {to_currency} not supported"}
                
        except Exception as e:
            print(f"❌ Error converting currency: {e}")
            return amount, {"error": str(e)}
    
    def get_supported_currencies(self) -> list[str]:
        """
        Get list of supported currencies
        """
        return list(self.fallback_rates.keys())
    
    async def get_currency_info(self, currency: str) -> Dict[str, str]:
        """
        Get information about a currency
        """
        currency_info = {
            "USD": {"name": "US Dollar", "symbol": "$"},
            "EUR": {"name": "Euro", "symbol": "€"},
            "GBP": {"name": "British Pound", "symbol": "£"},
            "JPY": {"name": "Japanese Yen", "symbol": "¥"},
            "CAD": {"name": "Canadian Dollar", "symbol": "C$"},
            "AUD": {"name": "Australian Dollar", "symbol": "A$"},
            "CHF": {"name": "Swiss Franc", "symbol": "CHF"},
            "CNY": {"name": "Chinese Yuan", "symbol": "¥"},
            "INR": {"name": "Indian Rupee", "symbol": "₹"},
            "KRW": {"name": "South Korean Won", "symbol": "₩"}
        }
        
        return currency_info.get(currency.upper(), {
            "name": currency.upper(),
            "symbol": currency.upper()
        })


# Global currency service instance
currency_service = CurrencyExchangeService()
