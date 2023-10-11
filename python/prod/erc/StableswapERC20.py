# StableswapERC20.py
# Author: Ian Moore ( imoore@syscoin.org )
# Date: Oct 2023

from python.prod.erc import ERC20

TKN_DECIMALS = 18

class StableswapERC20(ERC20):
    
    """ StableswapERC20 token

        Parameters
        ----------
        self.token_name : str
            Token name 
        self.token_addr : str
            Token address  
        self.token_total : float
            Token holdings 
        self.token_decimal : float
            Token decimal             
            
    """   
    def __init__(self, name: str, addr: str) -> None:
        self.token_name = name
        self.token_addr = addr
        self.token_total = 0
        self.token_decimal = TKN_DECIMALS
        self.type = 'composable_stable'
        
    def set_params(self, balance, token_decimal = None):
        self.token_total = balance
        self.token_decimal = TKN_DECIMALS if token_decimal == None else token_decimal
  
    def set_decimal(self, token_decimal):
        
        """ set_decimal

            Reset token decimal
                
            Parameters
            -------
            token_decimal : float
                token decimal     
        """         
        
        self.token_decimal = token_decimal 
