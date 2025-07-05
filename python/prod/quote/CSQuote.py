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

from ..cst.exchg.StableswapPoolMath import StableswapPoolMath 

GWEI_PRECISION = 18

class CSQuote():
    
    """ 
        Composable stable liquidity pool token quotes (ie, price, reserve and liquidity)
    """         
    
    def get_lp_from_amount(self, lp, tkn, tkn_amt_in):
        
        """ get_lp_from_amount

            Get amount of liquidity, given an amount of input token
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap LP    
            tkn: ERC20
                Token asset from CWPT set  
            amount_in: float
                Amount of input token             

            Returns
            -----------------
            lp_amt: float
                Amount of liquidity
        """         
        
        if(tkn_amt_in > 0):
            tkn_amts_in = [0]*len(lp.tkn_reserves)

            tkn_in_index = lp.get_tkn_index(tkn.token_name)
            dec_tkn_in = lp.tkn_decimals[tkn.token_name]
            tkn_in_dec = lp.amt2dec(tkn_amt_in, dec_tkn_in)

            tkn_amts_in[tkn_in_index] = tkn_in_dec
            out = lp.math_pool.calc_token_amount(tkn_amts_in)
            lp_amt = lp.dec2amt(out, GWEI_PRECISION)
        else:
            lp_amt = 0
        return lp_amt   
             
    
    