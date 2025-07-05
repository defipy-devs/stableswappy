# Copyright 2023–2025 Ian Moore
# Email: defipy.devs@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

from uniswappy import TokenDeltaModel
from uniswappy import EventSelectionModel

class RemoveLiquidity():
    
    """ Remove liquidity process

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

    def apply(self, lp, token_out, user_nm, amount_out):    
        
        """ apply

            Remove liquidity based on token or share amounts 
                
            Parameters
            -------
            lp : Exchange
                LP exchange
            token_out : ERC20
                specified ERC20 token               
            user_nm : str
                account name
            amount_out : float
                token amount to be swap             
                
            Returns
            -------
            out : float
                exchanged token amount               
        """ 

        out = lp.remove_liquidity(amount_out, token_out, user_nm)
        
        return out