const distlaimer = `
============================================================
WARNING: DO NOT USE IN PRODUCTION

This is example code, demonstrating the principles how
non-node code can interact with the Carbon SDK. THIS CODE
IS NOT SAFE. In particular, THIS CODE MAY ALLOW OTHERS
ACCESS TO THE WALLET LINKED TO THE SDK, especially if
they have access to the server and/or can establish an
http connection to it.
============================================================
`
import express from 'express';
import bodyParser from 'body-parser';
import { ethers } from 'ethers';
import { dispatch, initialize, signsubmittx, wallet, provider, signer } from "./sdkserver_dispatch.mjs";

const app = express()
const args = process.argv.slice(2);
const version = "0.9"
const date = "7/Mar/2022"

var   port  = 3118 // C=3, A=1, R=18 (Carbon)
var   token = "carbontoken"

app.use(bodyParser.json())

////////////////////////////// ROUTES //////////////////////////////
// root route
app.get('/', (req, res) => {
  res.send({
    msg: `Carbon SDK v${version} (${date})`,
    version: version,
    date: date
  })
})

//////////////////////////////
// asynchronous results storage
var resultsas = {}

//////////////////////////////
// route /api/scall [synchronous API]
app.post('/api/scall/:func', async (req, res) => {
  console.log(req.headers)
  if (req.headers['token']!==token){
    res.status(401).send('Unauthorized');
    return;
  }
  const func = req.params.func
  const body = req.body
  var retval

  console.log(`[api/scall/${func}] starting sync dispatch`)
  var [success, result] = dispatch(func, body)
  if (success == false) {
    retval = {success: false, error: `error calling dispatch with ${func} [${result}]`}
  } else {
    try {
      if (Array.isArray(result)) {
        result = await Promise.all(result)
      } else {
        result = await result
      }
      retval = {success: true, data: result}
      //console.log(`[api/scall/${func}] result=${retval.data}`)
    } catch (e) {
      retval = {success: false, error: e.message}
    }
  }
  res.send(retval)
  if (success){
    console.log(`[api/scall/${func}] result=${retval.data}`)
  }
})

//////////////////////////////
// route /api/ascall [asynchronous API]
app.post('/api/ascall/:func', async (req, res) => {
  if (req.headers['token']!==token){
    res.status(401).send('Unauthorized');
    return;
  }
  const func = req.params.func
  const body = req.body
  const reqid = Date.now()
  var retval, result

  console.log(`[api/ascall/${func}:${reqid}] starting async dispatch`)
  var [success, result] = dispatch(func, body)
  if (success == false) {
    retval = {success: false, error: `error calling dispatch with ${func} [${result}]`}
  } else {
    retval = {success: true, reqid: reqid}
    resultsas[reqid] = false
  }
  res.send(retval)
  try {
    result = await result
    resultsas[reqid] = {reqid: reqid, result: result}
    if (success){
      console.log(`[api/ascall/${func}:${reqid}] result=${result.result}`)  
    }
  } catch (e) {
    resultsas[reqid] = {reqid: reqid, result: {"error": e.message}}
  }

})

//////////////////////////////
// route GET /api/scall/result [result for asynchronous API]
app.get('/api/result/:reqid', (req, res) => {
  var result 

  if (req.headers['token']!==token){
    res.status(401).send('Unauthorized');
    return;
  }
  const reqid = req.params.reqid
  if (typeof resultsas[reqid] === 'undefined'){
    result = {success: false, error: `unknown reqid ${reqid}`, reqid: reqid, awaiting: false}
  } else if (resultsas[reqid] == false) {
    result = {success: false, error: `reqid ${reqid} not ready`, reqid: reqid, awaiting: true}
  }
  else {
    result = {success: true, data: resultsas[reqid]}
  }
  res.send(result)
})

//////////////////////////////
// route GET /api/addr [gets the wallet address]
app.get('/api/addr', (req, res) => {
  var result 

  if (req.headers['token']!==token){
    res.status(401).send('Unauthorized');
    return;
  }
  try{
    result = {success: true, data: wallet.address}
  } catch (e) {
    result = {success: false, error: `no wallet available`} 
  }
  res.send(result)
})

//////////////////////////////
// route POST /api/signsubmit [signs and submits the transaction]
app.post('/api/signsubmittx', async (req, res) => {
  
  const body = req.body
  if (req.headers['token']!==token){
    res.status(401).send('Unauthorized');
    return;
  }
  console.log("[api/signsubmittx] signing and submitting transaction")
  const txReceipt = await signsubmittx(body)
  res.send(txReceipt)
})

//////////////////////////////
// route POST /api/erc20/:func [various ERC20]
app.post('/api/erc20/:func', async (req, res) => {
  
  const func = req.params.func
  const p = req.body
  if (req.headers['token']!==token){
    res.status(401).send('Unauthorized');
    return;
  }
  const ERC20Abi = [
    'function balanceOf(address account) view returns (uint256)',
    'function decimals() view returns (uint8)',
    'function symbol() public view returns (string)',
  ];
  try {
    var result = []
    for (var i=0; i<p.tokens.length; i++){
      
      console.log(`[api/erc20/${func}] ${p.tokens[i]}`)
      var contract = new ethers.Contract(p.tokens[i], ERC20Abi, provider);
      switch (func) {

        case "decimals":
          var decimals = contract.decimals();
          result.push(decimals);
          break;
  
        case "symbol":
          var symbol = contract.symbol();
          result.push(symbol);
          break;
  
        case "balance_of":
          var balance = contract.balanceOf(p.address)
          result.push(balance);
          break;
    
        // case "transfer": 
        //   var txReceipt = contract.transfer(p.to, p.amount)
        //   res.send(txReceipt)
        //   break;
    
        case "approve":
          var txReceipt = contract.approve(p.to, p.amount)
          //res.send({success: true, data: txReceipt})
          break;
    
        // case "allowance":
        //   var allowance = await contract.allowance(p.owner, p.spender)
        //   res.send({success: true, data: allowance})
        //   break;
    
        // case "transferFrom":
        //   var txReceipt = await contract.transferFrom(p.from, p.to, p.amount)
        //   res.send({success: true, data: txReceipt})
        //   break;
    
        case "hello":
          result.push("hello world");
          break;
    
        default:
          break;
      }
    }
  
  } catch (e) {
    res.send({success: false, error: e.message})
  }
  res.send({success: true, data: await Promise.all(result)})
})



////////////////////////////// INITIALIZATION //////////////////////////////

// initializes the SDK, in particular calls the startDataSync() function
await initialize()
console.log(distlaimer)

// parse command line arguments
//console.log(args)
if (typeof args[0] !== "undefined"){
  port = parseInt(args[0])
}
if (typeof args[1] !== "undefined"){
  token = args[1]
}



const rpcUrl=process.env.SDKSERVER_RPCURL
const explorer=process.env.SDKSERVER_EXPLORER
const carbonui=process.env.SDKSERVER_UI
console.log(rpcUrl)
console.log(explorer)
console.log(carbonui)

////////////////////////////// RUN SERVER //////////////////////////////
// launch server
app.listen(port, () => {
  console.log(`SDK server listening on port ${port} [token=${token}]`)
})

