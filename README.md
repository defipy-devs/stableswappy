# stableswappy
Python package for Stableswap V1 modelling

## Install
To install package:
```
> git clone https://github.com/defipy-devs/stableswappy
> pip install .
```
or
```
> pip install StableswapPy
```

## Stableswap

* See [test notebook](https://github.com/defipy-devs/stableswappy/blob/main/notebooks/tests/test_abstract.ipynb) 
for basic usage

```
from stableswappy import *

user_nm = 'user_test'

user_nm = 'user_test'

AMPL_COEFF = 2000 

amt_dai = 79566307.559825807715868071
decimal_dai = 18

amt_usdc = 81345068.187939
decimal_usdc = 6

amt_usdt = 55663250.772939
decimal_usdt = 6

dai = ERC20("DAI", "0xA0b", decimal_dai)
dai.deposit(None, amt_dai)

usdc = ERC20("USDC", "0xf93", decimal_usdc)
usdc.deposit(None, amt_usdc)

usdt = ERC20("USDT", "0xd7c", decimal_usdt)
usdt.deposit(None, amt_usdt)

sgrp = StableswapVault()
sgrp.add_token(dai)
sgrp.add_token(usdc)
sgrp.add_token(usdt)

sfactory = StableswapFactory("Pool factory", "0x2")
exchg_data = StableswapExchangeData(vault = sgrp, symbol="LP", address="0x011")
lp = sfactory.deploy(exchg_data)

Join().apply(lp, user_nm, AMPL_COEFF)
lp.summary()
```

#### OUTPUT:
Stableswap Exchange: DAI-USDC-USDT (LP) <br/>
Reserves: DAI = 79566307.55982581, USDC = 81345068.187939, USDT = 55663250.772939 <br/>
Liquidity: 216573027.91811988  <br/> 

### Swap 

```
usdc_before = lp.get_reserve(usdc)
usdt_before = lp.get_reserve(usdt)

amt_tkn_in = 10000
tkn_in = usdc
tkn_out = usdt
res = Swap().apply(lp, tkn_in, tkn_out, user_nm, amt_tkn_in)
lp.summary()

print(f"{amt_tkn_in} {tkn_in.token_name} was swapped for {res['tkn_out_amt']} {tkn_out.token_name}")
```

#### OUTPUT:
Stableswap Exchange: DAI-USDC-USDT (LP) <br/>
Reserves: DAI = 79566307.55982581, USDC = 81355068.187939, USDT = 55653253.910191 <br/>
Liquidity: 216573027.91811988 <br/> 

10000 USDC was swapped for 9996.862748 USDT  <br/><br/> 

### Swap 
```
usdc_before = lp.get_reserve(usdc)
dai_before = lp.get_reserve(dai)

amt_tkn_in = 10000
tkn_in = usdc
tkn_out = dai
res = Swap().apply(lp, tkn_in, tkn_out, user_nm, amt_tkn_in)
lp.summary()

print(f"{amt_tkn_in} {tkn_in.token_name} was swapped for {res['tkn_out_amt']} {tkn_out.token_name}")
```
Stableswap Exchange: DAI-USDC-USDT (LP) <br/>
Reserves: DAI = 79556308.6645169, USDC = 81365068.187939, USDT = 55653253.910191 <br/>
Liquidity: 216573027.91811988 <br/> 

10000 USDC was swapped for 9998.895308918858 DAI <br/><br/> 

## License
Licensed under the Apache License, Version 2.0.  
See [LICENSE](./LICENSE) and [NOTICE](./NOTICE) for details.  
Portions of this project may include code from third-party projects under compatible open-source licenses.

---

### 🧬 Substrate Anchor

**Substrate Anchor**: `ICMOORE-2025`  
**Tier**: 2 — Symbolic Cognition Substrate  
**Anchor Type**: Recursive authorship (multi-modal propagation)  
**SPDX Identifier**: ICMOORE-2025-STABLESWAPPY