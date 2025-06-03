# Copyright [2025] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from uniswappy import TokenDeltaModel
from uniswappy import EventSelectionModel

class AddLiquidity():
     
    """ Add liquidity process

        Parameters
        ----------
        kind : Proc
            Type of swap proceedure
        ev : EventSelectionModel
            EventSelectionModel object to randomly generate buy vs sell events
        tDel : TokenDeltaModel
            TokenDeltaModel to randomly generate token amounts        
    """     

    def __init__(self, init_price = None, ev = None, tDel = None):
        self.ev = EventSelectionModel() if ev  == None else ev
        self.tDel = TokenDeltaModel(50) if tDel == None else tDel
        self.init_price = 1 if init_price == None else init_price

    def apply(self, lp, token_in, user_nm, amount_in):    
        
        """ apply

            Add liquidity based on token or share amounts
                
            Parameters
            -------
            lp : Exchange
                LP exchange
            token_in : ERC20
                specified ERC20 token               
            user_nm : str
                account name
            amount_in : float
                token amount to be swap             
                
            Returns
            -------
            out : float
                exchanged token amount               
        """ 

        out = lp.add_liquidity(amount_in, token_in, user_nm)
        
        return out