// the below fail was fixed by changing exports: "dist..." to exports: "./dist..."
import { Sdk } from "@bancor/carbon-sdk";
import { ethers } from "ethers";


//console.log(Sdk)
console.log("--------------------")

//const rpcUrl = 'https://eth-mainnet.alchemyapi.io/v2/token';
const explorer=process.env.SDKSERVER_EXPLORER
console.log(rpcUrl)
console.log(explorer)
const sdk = new Sdk({rpcUrl: rpcUrl});
//console.log(sdk)
console.log("--------------------")
console.log(sdk.isInitialized)
console.log("--------------------")
var startDataSync_promise = sdk.startDataSync()
console.log(startDataSync_promise)
console.log("--------------------")
// var i=0
// setInterval(function() {
//     i++
//     console.log(startDataSync_promise+" "+i)
//   }, 10000); // 10 seconds interval
startDataSync_promise = await startDataSync_promise
console.log(sdk.isInitialized)
console.log("--------------------")
const pairs = await sdk.pairs
//console.log(pairs)
console.log("--------------------")
const ETH   = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
const BNT   = '0x1f573d6fb3f13d689ff844b4ce37794d79a7ff1c'
const WBTC  = '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599'
const LINK  = '0x514910771af9ca656af840dff83e8264ecf986ca'
const DAI   = '0x6b175474e89094c44da98b954eedeac495271d0f'
const MATIC = '0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0'
const USDC  = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
const USDT  = '0xdac17f958d2ee523a2206206994597c13d831ec7'

const maxETHUSDC = await sdk.getMaxRateByPair(ETH, USDC)
const maxUSDCETH = await sdk.getMaxRateByPair(USDC, ETH)
const minETHUSDC = await sdk.getMinRateByPair(ETH, USDC)
const minUSDCETH = await sdk.getMinRateByPair(USDC, ETH)

console.log("maxETHUSDC: "+maxETHUSDC)
console.log("maxUSDCETH: "+maxUSDCETH)
console.log("minETHUSDC: "+minETHUSDC)
console.log("minUSDCETH: "+minUSDCETH)

const maxWBTCUSDC = await sdk.getMaxRateByPair(WBTC, USDC)
const maxUSDCWBTC = await sdk.getMaxRateByPair(USDC, WBTC)
const minWBTCUSDC = await sdk.getMinRateByPair(WBTC, USDC)
const minUSDCWBTC = await sdk.getMinRateByPair(USDC, WBTC)

console.log("maxWBTCUSDC: "+maxWBTCUSDC)
console.log("maxUSDCWBTC: "+maxUSDCWBTC)
console.log("minWBTCUSDC: "+minWBTCUSDC)
console.log("minUSDCWBTC: "+minUSDCWBTC)
console.log("--------------------")

const phrase="quiz super pitch label soon flash organ jaguar bridge tooth wrong feed"
const wallet = ethers.Wallet.fromMnemonic(phrase)
//const provider = new JsonRpcProvider(rpcUrl)
const provider = sdk._api._reader._contracts._provider
//console.log(sdk._api._reader._contracts._provider)
const signer = wallet.connect(provider)
const account = await signer.getAddress()
console.log("account: "+account)

var balance = await provider.getBalance(wallet.address);
// balance = BigInt(balance.toString())
// console.log(balance)
const balanceETH = ethers.utils.formatEther(balance)
console.log(`Latest balance Wei: ${balance}`);
console.log(`Latest balance ETH: ${balanceETH}`);
console.log("------------------")

const ERC20ABI = [
    {
      "constant": true,
      "inputs": [],
      "name": "totalSupply",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "name": "_owner",
          "type": "address"
        }
      ],
      "name": "balanceOf",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "_to",
          "type": "address"
        },
        {
          "name": "_value",
          "type": "uint256"
        }
      ],
      "name": "transfer",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "_from",
          "type": "address"
        },
        {
          "name": "_to",
          "type": "address"
        },
        {
          "name": "_value",
          "type": "uint256"
        }
      ],
      "name": "transferFrom",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]

const USDCc = new ethers.Contract(USDC, ERC20ABI, provider);
const USDCbalance = await USDCc.balanceOf(account);
console.log(`USDC: ${USDCbalance.toString()} token Wei`);

const DAIc = new ethers.Contract(DAI, ERC20ABI, provider);
const DAIbalance = await DAIc.balanceOf(account);
console.log(`DAI: ${DAIbalance.toString()} token Wei`);

const WBTCc = new ethers.Contract(WBTC, ERC20ABI, provider);
const WBTCbalance = await WBTCc.balanceOf(account);
console.log(`WBTC: ${WBTCbalance.toString()} token Wei`);
console.log("------------------")

var strategy, signedStrategy, txReceipt
// strategy = await sdk.createBuySellStrategy(ETH, USDC, 
//     "17000", "18000", "30000", 
//     "23000", "24000", "2")
// signedStrategy = await wallet.signTransaction(strategy);
// txReceipt = await signer.sendTransaction(signedStrategy);
// console.log(txReceipt)

strategy = await sdk.createBuySellStrategy(ETH, DAI, 
    "17000", "18000", "0", 
    "23000", "24000", "2")
console.log(strategy)

