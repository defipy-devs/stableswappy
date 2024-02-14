# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

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
             
    
    