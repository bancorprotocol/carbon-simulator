import *  as tl from "./sdkserver_testlib.mjs"
import { Sdk } from "@bancor/carbon-sdk";
import { ethers } from 'ethers';

const rpcUrl=process.env.SDKSERVER_RPCURL
const TENDERLY = true
const sdk = new Sdk({rpcUrl: rpcUrl});

// initialize the wallet (if secret data is available)
export var wallet
export var signer
export var provider

function n(endpoint){
    // converts camel case to snake case
    // e.g. "getMatchActions" -> "get_match_actions"
    return endpoint.replace(/([A-Z])/g, '_$1').toLowerCase();
}

function a(addr){
    // converts address to checksum address
    const csaddr = ethers.utils.getAddress(addr)
    console.log(csaddr)
    return csaddr
}

async function niyas(){
    return {result: "not implemented yet [async]"}
}

function niys(){
    return {result: "not implemented yet [sync]"}
}

export async function initialize(){
    const sdkServerMnemomicPhrase = process.env.SDKSERVER_MEMONICPHRASE;
    if (typeof sdkServerMnemomicPhrase !== "undefined"){
    try{
        wallet = ethers.Wallet.fromMnemonic(sdkServerMnemomicPhrase)
    } catch (e) {
        wallet = ethers.Wallet.fromPhrase(sdkServerMnemomicPhrase)
    }
    console.log("----------------------------------------------------------------------")
    console.log(`SDK server wallet: ${wallet.address}`)
    console.log("----------------------------------------------------------------------")
    } else {
        console.log("WARNING: no mnemonic phrase found in environment variable SDKSERVER_MEMONICPHRASE")
        console.log("run `source /Volumes/Private/bin/sdkserver` in the terminal before launching the server")
    }
    provider = sdk._api._reader._contracts._provider
    if (TENDERLY){
        signer = provider.getUncheckedSigner(wallet.address);
    } else {
        signer = wallet.connect(provider)
    }
    console.log("----------------------------------------------------------------------")
    console.log("[initialize] calling startDataSync")
    console.log("----------------------------------------------------------------------")
    var result = await sdk.startDataSync();
    console.log("----------------------------------------------------------------------")
    console.log("[initialize] data sync finished")
    console.log("----------------------------------------------------------------------")
}

export async function signsubmittx(p){
    const tx = p.tx
    const sign = p.sign
    var signedTx
    if (sign){
        try {
            if (TENDERLY){
                signedTx = tx
              } else {
                signedTx = await signer.signTransaction(tx);
            }
        } catch(e) {
            return {success: false, error: `signing failed ${e}`}
        }

    } else {
        signedTx = tx
    }
    var txReceipt
    try {
        txReceipt = await signer.sendTransaction(signedTx);
    } catch(e) {
        return {success: false, error: `submitting transaction failed ${e}`}
    }
    return {success: true, data: {txReceipt: txReceipt}}
}

export function dispatch(func, p){
    var result, success = true
    //console.log("[dispatch] "+func)

    try{
        switch(func) {

            ////////////////////////////////////////////////////
            // functions defined in testlib.js (mul, plus, qmul, qplus)
            case "plus":
            result = tl.plus(p.a, p.b);
            break;
    
            case "mul":
            result = tl.mul(p.a, p.b);
            break;
    
            case "qplus":
                result = Promise.resolve(tl.qplus(p.a, p.b));
                break;
    
            case "qmul":
                result = Promise.resolve(tl.qmul(p.a, p.b));
                break;
    
    
            ////////////////////////////////////////////////////
            // functions defined in the actual SDK
    
            // public static getMatchActions(
            //     amountWei: string,
            //     tradeByTargetAmount: boolean,
            //     orders: OrdersMap
            //   ): MatchAction[]
            case n("getMatchActions"):
                result = Promise.resolve(niys());
                //result = Promise.resolve(getMatchActions(p.amountWei, p.tradeByTargetAmount, p.orders));
                break;
    
            // // public async startDataSync(): Promise<void>
            // case n("startDataSync"):
            //     //result = niyas();
            //     result = sdk.startDataSync();
            //     break;
    
            // // public get isInitialized(): boolean
            // case n("isInitialized"):
            //     //result = Promise.resolve(niys());
            //     result = Promise.resolve(sdk.isInitialized);
            //     break;
    
            // public get pairs(): TokenPair[]
            case n("pairs"):
                //result = Promise.resolve(niys());
                result = Promise.resolve(sdk.pairs);
                break;
    
            // public hasLiquidityByPair(sourceToken: string, targetToken: string): boolean
            case n("hasLiquidityByPair"):
                console.log(p.pairList, typeof(p.pairList))
                if (p.pairList !== undefined){
                    result = []
                    for (var i = 0; i < p.pairList.length; i++){
                        var pair = p.pairList[i]
                        result.push(sdk.hasLiquidityByPair(a(pair.sourceToken), a(pair.targetToken)))
                    }
                    result = Promise.resolve(result)
                    break;
                }
                result = Promise.resolve(sdk.hasLiquidityByPair(a(p.sourceToken), a(p.targetToken)));
                break;
    
            // public async getLiquidityByPair(
            //     sourceToken: string,
            //     targetToken: string
            //   ): Promise<string>
            case n("getLiquidityByPair"):
                result = sdk.getLiquidityByPair(a(p.sourceToken), a(p.targetToken));
                break;
    
            // public async getUserStrategies(user: string): Promise<Strategy[]> 
            case n("getUserStrategies"):
                result = sdk.getUserStrategies(p.user);
                break;
    
            // public async getMatchParams(
            //     sourceToken: string,
            //     targetToken: string,
            //     amount: string,
            //     tradeByTargetAmount: boolean
            //   ): Promise<{
            //     orders: OrdersMap;
            //     amountWei: string;
            //     sourceDecimals: number;
            //     targetDecimals: number;
            //   }>
            case n("getMatchParams"):
                result = sdk.getMatchParams(a(p.sourceToken), a(p.targetToken), p.amount, p.tradeByTargetAmount);
                break;
    
            // public async getTradeData(
            //     sourceToken: string,
            //     targetToken: string,
            //     amount: string,
            //     tradeByTargetAmount: boolean,
            //     filter?: (rate: Rate) => boolean
            //   ): Promise<{
            //     tradeActions: TradeActionStruct[];
            //     actionsTokenRes: Action[];
            //     totalSourceAmount: string;
            //     totalTargetAmount: string;
            //     effectiveRate: string;
            //     actionsWei: MatchAction[];
            //   }>
            case n("getTradeData"):
                result = sdk.getTradeData(a(p.sourceToken), a(p.targetToken), p.amount, p.tradeByTargetAmount, p.filter);
                break;
    
            // public async getTradeDataFromActions(
            //     sourceToken: string,
            //     targetToken: string,
            //     tradeByTargetAmount: boolean,
            //     actionsWei: MatchAction[]
            //   ): Promise<{
            //     tradeActions: TradeActionStruct[];
            //     actionsTokenRes: Action[];
            //     totalSourceAmount: string;
            //     totalTargetAmount: string;
            //     effectiveRate: string;
            //     actionsWei: MatchAction[];
            //   }>
            case n("getTradeDataFromActions"):
                result = sdk.getTradeDataFromActions(a(p.sourceToken), a(p.targetToken), p.tradeByTargetAmount, p.actionsWei);
                break;
    
            // public async composeTradeByTargetTransaction(
            //     sourceToken: string,
            //     targetToken: string,
            //     tradeActions: TradeActionStruct[],
            //     deadline: BigNumberish,
            //     maxInput: string,
            //     overrides?: PayableOverrides
            //   ): Promise<PopulatedTransaction>
            case n("composeTradeByTargetTransaction"):
                result = sdk.composeTradeByTargetTransaction(a(p.sourceToken), a(p.targetToken), p.tradeActions, p.deadline, p.maxInput, p.overrides);
                break;
    
            // public async composeTradeBySourceTransaction(
            //     sourceToken: string,
            //     targetToken: string,
            //     tradeActions: TradeActionStruct[],
            //     deadline: BigNumberish,
            //     minReturn: string,
            //     overrides?: PayableOverrides
            //   ): Promise<PopulatedTransaction>
            case n("composeTradeBySourceTransaction"):
                result = sdk.composeTradeBySourceTransaction(a(p.sourceToken), a(p.targetToken), p.tradeActions, p.deadline, p.minReturn, p.overrides);
                break;
    
            // public async createBuySellStrategy(
            //     baseToken: string,
            //     quoteToken: string,
            //     buyPriceLow: string,
            //     buyPriceHigh: string,
            //     buyBudget: string,
            //     sellPriceLow: string,
            //     sellPriceHigh: string,
            //     sellBudget: string,
            //     overrides?: PayableOverrides
            //   ): Promise<PopulatedTransaction>
            case n("createBuySellStrategy"):
                //result = niyas();
                result = sdk.createBuySellStrategy(a(p.baseToken), a(p.quoteToken), p.buyPriceLow, p.buyPriceHigh, p.buyBudget, p.sellPriceLow, p.sellPriceHigh, p.sellBudget, p.overrides);
                break;
    
            // public async updateStrategy(
            //     strategyId: BigNumberish,
            //     encoded: EncodedStrategy,
            //     baseToken: string,
            //     quoteToken: string,
            //     {
            //       buyPriceLow,
            //       buyPriceHigh,
            //       buyBudget,
            //       sellPriceLow,
            //       sellPriceHigh,
            //       sellBudget,
            //     }: StrategyUpdate,
            //     buyMarginalPrice?: MarginalPriceOptions | string,
            //     sellMarginalPrice?: MarginalPriceOptions | string,
            //     overrides?: PayableOverrides
            //   ): Promise<PopulatedTransaction>
            case n("updateStrategy"):
                result = niyas();
                //result = sdk.updateStrategy(p.strategyId, p.encoded, a(p.baseToken), a(p.quoteToken), p.update, p.buyMarginalPrice, p.sellMarginalPrice, p.overrides);
                break;
    
            // public deleteStrategy(
            //     strategyId: BigNumberish
            //     ): Promise<PopulatedTransaction>
            case n("deleteStrategy"):
                //result = niyas();
                result = sdk.deleteStrategy(p.strategyId, p.overrides);
                break;
    
            // public async getRateLiquidityDepthByPair(
            //     sourceToken: string,
            //     targetToken: string,
            //     rate: string
            //   ): Promise<string> 
            case n("getRateLiquidityDepthByPair"):
                var srca = a(p.sourceToken)
                var trga = a(p.targetToken)
                console.log("p.rate", p.rate);
                    
                if (Array.isArray(p.rate)) {
                    result = []
                    for (let i = 0; i < p.rate.length; i++) {
                        let rate = p.rate[i];
                        console.log("rate", rate)
                        result.push(sdk.getRateLiquidityDepthByPair(srca, trga, rate));
                    }
                } else {
                    result = sdk.getRateLiquidityDepthByPair(srca, trga, p.rate);
                }
                break;
    
            // public async getMinRateByPair(
            //     sourceToken: string,
            //     targetToken: string
            //   ): Promise<string>
            case n("getMinRateByPair"):
                result = sdk.getMinRateByPair(a(p.sourceToken), a(p.targetToken));
                break;
    
            // public async getMaxRateByPair(
            //     sourceToken: string,
            //     targetToken: string
            //   ): Promise<string> 
            case n("getMaxRateByPair"):
                result = sdk.getMaxRateByPair(a(p.sourceToken), a(p.targetToken));
                break;
    
    
            ////////////////////////////////////////////////////
            // default
            default:
                success = false
                result = {error: "unknown method"}
        }
    } catch(error){
        console.log(error)
        success = false
        result = {error: error.message}
    }
    console.log("[dispatch] result: ", result)
    return [success, result]
  }

// module.exports = {
//     dispatch: dispatch
//     }
