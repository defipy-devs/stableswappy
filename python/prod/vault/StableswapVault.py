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

import numpy as np
from decimal import Decimal
from ..erc import ERC20

class StableswapVault:
    
    """ 
        Create Stableswap vault for pool token management
        
        Parameters
        ---------------
        self.tkns : list
            List of ERC20 tokens within vault
        self.tkn_dic : dictionary
            Dictionary of ERC20 tokens within vault referenced by token name         
    """     
  
    def __init__(self) -> None:
        self.tkns = []
        self.tkn_dic = {}            
        
    def add_token(self, tkn: ERC20):
        
        """ add_token

            Deploy a Stableswap liquidity pool (LP) exchange
                
            Parameters
            -----------------
            tkn : ERC20
                ERC20 token                  
        """           
        
        if tkn.token_name not in self.tkn_dic:    
            self.tkns.append(tkn) 
            self.tkn_dic[tkn.token_name] = tkn
        else:
            print('ERROR: token already exists within group')

    def check_tkn(self, tkn):
        
        """ check_tkn

            Check if ERC20 token is in vault
                
            Parameters
            -----------------
            tkn : ERC20
                ERC20 token
                
            Returns
            -----------------
            contains : boolean
                Indicator of whether token is contained in vault                         
        """            
        
        tkn_nms = self.get_names()
        return tkn.token_name in tkn_nms         
            
    def get_name(self):
        
        """ get_name

            Get token names
                
            Returns
            -----------------
            tkn_nms : str
                Token names delimited by hyphen
        """             
        
        tkn_nms = self.get_names()
        return "-".join(tkn_nms)  
    
    def get_coins_str(self):
        tkn_nms = self.get_names()
        return "-".join(tkn_nms)    
 
    def get_token(self, tkn_name):
        
        """ get_token

            Get token from vault given its name symbol
            
            Parameters
            -----------------
            tkn_name : str
                Token name symbol            
                
            Returns
            -----------------
            tkn : ERC20
                Retrieved ERC20 token
        """             
        
        return self.tkn_dic[tkn_name]

    def get_tokens(self):
        
        """ get_tokens

            Get list of tokens
                    
            Returns
            -----------------
            tkns : list
                List of tokens
        """            
        
        return self.tkns
    
    def get_names(self):
        
        """ get_names

            Get token string names
                    
            Returns
            -----------------
            tkn_nms : list
                Token string names
        """             
        
        tkn_nms = []
        for tkn in self.tkns:
            tkn_nms.append(tkn.token_name) 
        return tkn_nms    
    
    def get_dict(self):
        
        """ get_dict

            Get dictionary of tokens referened by token name
                    
            Returns
            -----------------
            tkn_dict : dict
                Dictionary of tokens
        """         
        
        tkn_dict = {}
        for tkn in self.tkns:
            tkn_dict[tkn.token_name] = tkn
        return tkn_dict      
    
    def get_balances(self):
        
        """ get_balances

            Get dictionary of token balances referened by token name
                    
            Returns
            -----------------
            tkn_balances : dict
                Dictionary of token balances
        """          
        
        tkn_balances = {}
        for tkn in self.tkns:
            tkn_balances[tkn.token_name] = tkn.token_total
        return tkn_balances   
            
    def get_decimals(self):
        
        """ get_decimals

            Get dictionary of token decimals referenced by token name
                    
            Returns
            -----------------
            norm_wts_dict : dict
                Dictionary of token decimals
        """            
        
        tkn_decimals = {}
        for tkn in self.tkns:
            tkn_decimals[tkn.token_name] = tkn.token_decimal
        return tkn_decimals  
    
    def get_rates(self):
        
        """ get_rates

            Get dictionary of token rates referenced by token name
                    
            Returns
            -----------------
            tkn_rates : dict
                Dictionary of token rates
        """           
        
        tkn_rates = {}
        for tkn_nm in self.tkn_dic:
            tkn = self.tkn_dic[tkn_nm]
            tkn_rates[tkn.token_name] = self.rate_multiplier(tkn.token_decimal) 
        return tkn_rates 
    
    def get_decimal_amts(self):
        
        """ get_decimal_amts

            Get dictionary of token amounts in decimal format
                    
            Returns
            -----------------
            decimal_amts : dict
                Dictionary of token amounts in decimal format
        """         
        
        decimal_amts = {}
        token_decimals = self.get_decimals()
        for tkn_nm in token_decimals:
            tkn = self.get_token(tkn_nm)
            decimal_amts[tkn.token_name] = self.amt2dec(tkn.token_total, tkn.token_decimal) 
        return decimal_amts  
    
    def amt2dec(self, tkn_amt, decimal):
        
        """ amt2dec

            Convert token amount to decimal
                    
            Returns
            -----------------
            tkn_amt : float
                Token amount
            decimal : int
                Decimals               
        """           
        
        return int(Decimal(str(tkn_amt))*Decimal(str(10**decimal)))    
    
    def rate_multiplier(self, decimals):
        return 10 ** (36 - decimals)    