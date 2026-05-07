from decimal import Decimal
import pandas as pd

import asyncio
import aiohttp


curr_list = [
    "ACH",
    "AEVO",
    "AGLD",
    "AVAIL",
    "BBL",
    "BTC",
    "CATS",
    "CGPT",
    "COOKIE",
    "CPOOL",
    "CSPR",
    "DEFI",
    "DEGEN",
    "ENJ",
    "ETHW",
    "FORT",
    "FXS",
    "GODS",
    "GST",
    "GTAI",
    "HFT",
    "HNT",
    "HTX",
    "JST",
    "L3",
    "LADYS",
    "LMWR",
    "LRC",
    "MAVIA",
    "MOCA",
    "MOVR",
    "MYRIA",
    "MYRO",
    "NAKA",
    "NAVX",
    "NFT",
    "NYM",
    "OMG",
    "PIP",
    "RACA",
    "RATS",
    "REN",
    "RPL",
    "SAROS",
    "SATS",
    "SCA",
    "SCR",
    "SD",
    "SMILE",
    "SOCIAL",
    "SSV",
    "SUNDOG",
    "SWELL",
    "TEL",
    "TIME",
    "TOMI",
    "VANRY",
    "VELO",
    "VRA",
    "VRTX",
    "WEMIX",
    "WEN",
    "X",
    "XAI",
    "XETA",
    "XTZ",
    "ZETA",
    "ZK",
    "ZKF",
]


async def get_bybit(data: list) -> dict:
    async with aiohttp.ClientSession() as session:
        total = {}
        for i in data:
            params = {"category": "spot", "symbol": f"{i}USDT"}
            async with session.get(
                "https://api.bybit.com/v5/market/tickers", params=params
            ) as response:
                try:
                    dict_data_bybit = await response.json()
                    total[f"{i}_USDT"] = [
                        "Bybit",
                        Decimal(dict_data_bybit["result"]["list"][0]["lastPrice"]),
                        Decimal(dict_data_bybit["result"]["list"][0]["bid1Price"]),
                        Decimal(dict_data_bybit["result"]["list"][0]["ask1Price"]),
                    ]
                except:
                    print("Couldn't receive a pair")
                else:
                    print("A pair has been collected")

    print("Bybit has been collected")
    return total


async def get_mexc(data: list) -> dict:
    async with aiohttp.ClientSession() as session:
        total = {}
        for i in data:
            params = {"symbol": f"{i}USDT"}
            async with session.get(
                "https://api.mexc.com/api/v3/ticker/24hr", params=params
            ) as response:
                try:
                    dict_data_mexc = await response.json()
                    total[f"{i}_USDT"] = [
                        "Mexc",
                        Decimal(dict_data_mexc["lastPrice"]),
                        Decimal(dict_data_mexc["bidPrice"]),
                        Decimal(dict_data_mexc["askPrice"]),
                    ]
                except:
                    print("Couldn't receive a pair")
                else:
                    print("A pair has been collected")

    print("Mexc has been collected")
    return total


async def get_bitget(data: list) -> dict:
    """Receiving a dict from requests"""
    async with aiohttp.ClientSession() as session:
        total = {}
        for i in data:
            params = {"symbol": f"{i}USDT"}
            async with session.get(
                "https://api.bitget.com/api/v2/spot/market/tickers", params=params
            ) as response:
                try:
                    dict_data_bitget = await response.json()
                    total[f"{i}_USDT"] = [
                        "Bitget",
                        Decimal(dict_data_bitget["data"][0]["lastPr"]),
                        Decimal(dict_data_bitget["data"][0]["bidPr"]),
                        Decimal(dict_data_bitget["data"][0]["askPr"]),
                    ]
                except:
                    print("Couldn't receive a pair")
                else:
                    print("A pair has been collected")

    print("Bitget has been collected")
    return total


async def get_kucoin(data: list) -> dict:
    """Receiving a dict from requests"""
    async with aiohttp.ClientSession() as session:
        total = {}
        for i in data:
            params = {"symbol": f"{i}-USDT"}
            async with session.get(
                "https://api.kucoin.com/api/v1/market/stats", params=params
            ) as response:
                try:
                    dict_data_kucoin = await response.json()
                    total[f"{i}_USDT"] = [
                        "KuCoin",
                        Decimal(dict_data_kucoin["data"]["last"]),
                        Decimal(dict_data_kucoin["data"]["sell"]),
                        Decimal(dict_data_kucoin["data"]["buy"]),
                    ]
                except:
                    print("Couldn't receive a pair")
                else:
                    print("A pair has been collected")

    print("Kucoin has been collected")
    return total


async def main(data):
    bybit, mexc, bitget, kucoin = await asyncio.gather(
        get_bybit(data),
        get_mexc(data),
        get_bitget(data),
        get_kucoin(data),
    )

    min_all = {}
    max_all = {}
    value_cur = {}
    spread_list = []

    for i in curr_list:
        if (
            f"{i}_USDT" in bybit
            and f"{i}_USDT" in mexc
            and f"{i}_USDT" in bitget
            and f"{i}_USDT" in kucoin
        ):
            value_cur[f"{i}_USDT"] = (
                [bybit[f"{i}_USDT"]]
                + [mexc[f"{i}_USDT"]]
                + [bitget[f"{i}_USDT"]]
                + [kucoin[f"{i}_USDT"]]
            )
            max_cur = max(value_cur[f"{i}_USDT"], key=lambda x: x[1])
            min_cur = min(value_cur[f"{i}_USDT"], key=lambda x: x[1])
            spread = str(round(((max_cur[3] - max_cur[2]) / max_cur[3] * 100), 2)) + "%"
            if not "-" in spread:
                spread = "+" + spread
            min_all[f"{i}_USDT"] = min_cur[:2]
            max_all[f"{i}_USDT"] = max_cur[:2]
            spread_list.append(spread)

    df1 = pd.DataFrame(spread_list)
    df2 = pd.DataFrame(min_all, index=["Биржа", "Курс(Min)"])
    df3 = pd.DataFrame(max_all, index=["Биржа", "Курс(Max)"])

    with pd.ExcelWriter("Связки валют.xlsx") as file:
        df2 = df2.T
        df3 = df3.T
        df1.to_excel(
            file, index=False, startcol=3, header=["Spread"], sheet_name="Связки валют"
        )
        df2.to_excel(file, index=True, startcol=0, sheet_name="Связки валют")
        df3.to_excel(file, index=False, startcol=4, sheet_name="Связки валют")


if __name__ == "__main__":
    asyncio.run(main(curr_list))
    print("Success")
