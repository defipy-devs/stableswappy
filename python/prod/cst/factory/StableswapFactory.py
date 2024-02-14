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
    
    """ 
        Create Stableswap liquidity pools for given token sets
        
        Parameters
        ---------------
        self.name : str
            Token name 
        self.address : str
            Address name                   
    """         
      
    def __init__(self, name: str, address: str) -> None:
        self.name = name
        self.address = address
        self.exchange_from_token = {}
        self.token_from_exchange = {} 
        self.parent_lp = None
        
    def deploy(self, exchg_data : StableswapExchangeData):   
        
        """ deploy

            Deploy a Stableswap liquidity pool (LP) exchange
                
            Parameters
            -----------------
            exchg_data : StableswapExchangeData
                Exchange initialization data     

            Returns
            -----------------
            exchange : StableswapExchange
                Newly created exchange that is also a LP token                    
        """           
        
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
        
        """ get_exchange

            Get exchange from given token
                
            Parameters
            -----------------
            token : ERC20
                receiving user address      
                
            Returns
            -----------------
            exchange : StableswapExchange
                exchange from mapped token                    
        """          
        
        return self.exchange_from_token.get(token)

    def get_token(self, exchange):       
        
        """ get_token

            Get token set from exchange
                
            Parameters
            -----------------
            exchange : StableswapExchange
                receiving user address      
                
            Returns
            -----------------
            token : ERC20 
                token from mapped exchange                     
        """           
        
        return self.token_from_exchange.get(exchange)
