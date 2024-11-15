from dataclasses import dataclass
import requests
import json
from typing import List, Dict, Union

@dataclass
class Website:
  url: str

@dataclass
class Social:
  platform: str
  handle: str

@dataclass
class Info:
  imageUrl: str
  websites: List[Website]
  socials: List[Social]

@dataclass
class Liquidity:
  usd: float
  base: float
  quote: float

@dataclass
class Token:
  address: str
  name: str
  symbol: str

@dataclass
class Pair:
  chainId: str
  dexId: str
  url: str
  pairAddress: str
  labels: List[str]
  baseToken: Token
  quoteToken: Token
  priceNative: str
  priceUsd: str
  liquidity: Liquidity
  fdv: float
  marketCap: float
  info: Info
  boosts: dict

@dataclass
class DexScreenerCoinInfo:
  schemaVersion: str
  pairs: List[Pair]


async def get_coin_info(hash_ids: List[str]) -> Union[DexScreenerCoinInfo, None]:
  """
  Fetches coin information for a list of hash IDs asynchronously.

  Args:
      hash_ids: A list of Solana hash identifiers for coins.

  Returns:
      A Promise that resolves to a DexScreenerCoinInfo object containing 
      information for all requested coins, or None if there's an error.
  """
  all_coins = ",".join(hash_ids)
  url = f"https://api.dexscreener.com/latest/dex/tokens/{all_coins}"

  print(f"Checking for {url}")

  response = requests.get(url)

  if response.status_code == 200:
    try:
      data = json.loads(response.text)
      pairs = DexScreenerCoinInfo(**data).pairs
      return pairs[0] if pairs and len(pairs) > 0 else None
    except json.JSONDecodeError:
      print(f"Error parsing JSON response from {url}")
      return None
    except requests.exceptions.RequestException as e:
      print(f"Error fetching data from {url}: {e}")
      return None
  else:
    print(f"API request failed with status code: {response.status_code}")
    return None