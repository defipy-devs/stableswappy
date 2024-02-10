# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ...erc import ERC20
from ..exchg import StableswapExchange 
from ...utils.interfaces import IExchangeFactory 
from ...utils.data import StableswapExchangeData
from ...utils.data import FactoryData
from ...vault import StableswapVault

class StableswapFactory:
      
    def __init__(self, name: str, address: str) -> None:
        self.name = name
        self.address = address
        self.exchange_from_token = {}
        self.token_from_exchange = {} 
        self.parent_lp = None
        
    def deploy(self, exchg_data : StableswapExchangeData):   
        
        vault = exchg_data.vault
        symbol = exchg_data.symbol
        address = exchg_data.address        
     
        assert symbol not in self.token_from_exchange, 'StableswapFactory: EXCHANGE_CREATED'   
            
        factory_struct = FactoryData(self.token_from_exchange,  self.parent_lp, self.name, self.address)
        exchg_struct = StableswapExchangeData(vault = vault, symbol=symbol, address=address)
        exchange = StableswapExchange(factory_struct, exchg_struct)             
            
        self.exchange_from_token[vault.get_name()] = exchange
        self.token_from_exchange[exchange.name] = vault.get_dict()
        
        return exchange  
    
    def get_exchange(self, token):
        
        return self.exchange_from_token.get(token)

    def get_token(self, exchange):       
        
        return self.token_from_exchange.get(exchange)
