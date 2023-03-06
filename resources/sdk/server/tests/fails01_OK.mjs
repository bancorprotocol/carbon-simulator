// the below fail was fixed by changing exports: "dist..." to exports: "./dist..."
import { Sdk } from "@bancor/carbon-sdk";
import { ethers } from "ethers";
//const rpcUrl = "https://rpc.tenderly.co/fork/cbb1b...";
//const explorer="https://dashboard.tenderly.co/fork/cbb1b..."
const rpcUrl=process.env.SDKSERVER_RPCURL
const explorer=process.env.SDKSERVER_EXPLORER
console.log(rpcUrl)
console.log(explorer)

const sdk = new Sdk({rpcUrl: rpcUrl});
const ETH   = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
const USDC  = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
const TENLY = true
console.log("--------------------")

await sdk.startDataSync()
console.log(sdk.isInitialized)
console.log("--------------------")

const phrase="quiz super pitch label soon flash organ jaguar bridge tooth wrong feed"
const wallet = ethers.Wallet.fromMnemonic(phrase)
const provider = sdk._api._reader._contracts._provider
const account = await wallet.getAddress()
console.log("account: "+account)
var signer
if (TENLY){
  signer = provider.getUncheckedSigner(account);
} else {
  signer = wallet.connect(provider)
}
console.log(signer)


const balance = await provider.getBalance(wallet.address);
const balanceETH = ethers.utils.formatEther(balance)
console.log(`Latest balance Wei: ${balance}`);
console.log(`Latest balance ETH: ${balanceETH}`);
console.log("------------------")

var strategy, signedStrategy, txReceipt
const unsignedStrategy = await sdk.createBuySellStrategy(ETH, USDC, 
    "1234", "1235", "2456", 
    "2345", "2346", "2", 
    { gasLimit: 999999999 }
)
if (TENLY){
  signedStrategy = unsignedStrategy
} else {
  signedStrategy = await signer.signTransaction(unsignedStrategy);
}
console.log(signedStrategy)
txReceipt = await signer.sendTransaction(signedStrategy);
console.log(txReceipt)
// console.log(txReceipt)

// strategy = await sdk.createBuySellStrategy(ETH, DAI, 
//     "17000", "18000", "0", 
//     "23000", "24000", "2")
// console.log(strategy)
console.log("BYE---------------")
