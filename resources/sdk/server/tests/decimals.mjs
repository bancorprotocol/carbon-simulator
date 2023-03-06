import { ethers } from 'ethers';
import { ERC20ABI } from '../lib/erc20abi.mjs';

// set ALCHEMY_RPCURL running `source /Volumes/Private/bin/secrets`
const rpcUrl = process.env.ALCHEMY_RPCURL;
const provider = new ethers.providers.JsonRpcProvider(rpcUrl);
const contractAddress = '0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9'; // replace with the contract address of the ERC20 token
const abi = ['function decimals() view returns (uint8)']; // replace with the ABI of the ERC20 contract
const contract = new ethers.Contract(contractAddress, abi, provider);
const decimals = await contract.decimals();
console.log(`Decimals: ${decimals}`);

const tokens = ['0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9',
'0x27702a26126e0b3702af63ee09ac4d1a084ef628',
'0x960b236a07cf122663c4303350609a66a7b288c0',
'0xba100000625a3754423978a60c9317c58a424e3d',
'0xba11d00c5f74255f56a5e366f4f77f5a186d7f55',
'0x0d8775f648430679a709e98d2b0cb6250d2887ef',
'0xb8c77482e45f1f44de1745f52c74426c631bdd52',
'0x1f573d6fb3f13d689ff844b4ce37794d79a7ff1c',
'0x4fabb145d64652a948d72533023f6e7a623c7c53',
'0x56d811088235f11c8920698a204a5010a788f4b3',
'0xaaaebe6fe48e54f431b0c390cfaf0b017d09d42d',
'0x4ecb692b0fedecd7b486b4c99044392784877e8c',
'0xc00e94cb662c3520282e6f5717214004a7f26888',
'0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b',
'0xd533a949740bb3306d119cc777fa900ba034cd52',
'0x6b175474e89094c44da98b954eedeac495271d0f',
'0xa1d65e8fb6e87b60feccbc582f7f97804b725521',
'0xbf2179859fc6d5bee9bf9158632dc51678a4100e',
'0xf629cbd94d3791c9250152bd8dfbdf380e2a3b9c',
'0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
'0x178c820f862b14f316509ec36b13123da19a6054',
'0x50d1c9771902476076ecfc8b2a83ad6b9355a4c9',
'0x6810e776880c02933d47db1b9fc05908e5386b96',
'0x056fd409e1d7a124bd7017459dfea2f387b6d5cd',
'0x8a9c67fee641579deba04928c4bc45f66e26343a',
'0xdd974d5c2e2928dea5f71b9825b8b646686bd200',
'0x80fb784b7ed66730e8b1dbd9820afd29931aab03',
'0x514910771af9ca656af840dff83e8264ecf986ca',
'0xbbbbca6a901c926f240b89eacb641d8aec7aeafd',
'0x0f5d2fb29fb7d3cfee444a200298f468908cc942',
'0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0',
'0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2',
'0xec67005c4e498ec7f55e092bd1d35cbc47c91892',
'0xa3bed4e1c75d00fa6f4e5e6922db7261b5e9acd2',
'0x1776e1f26f98b1a5df9cd347953a26dd3cb46671',
'0x967da4048cd07ab37855c090aaf366e4ce1b9f48',
'0xd26114cd6ee289accf82350c8d8487fedb8a0c07',
'0x5228a22e72ccc52d415ecfd199f99d0665e7733b',
'0xfca59cd816ab1ead66534d82bc21e7515ce441cf',
'0x408e41876cccdc0f92210600ef50372656052a38',
'0xeb4c2781e4eba804ce9a9803c67d0893436bb27d',
'0x1c5db575e2ff833e46a2e9864c22f4b22e0b37c2',
'0xb4efd85c19999d84251304bda99e90b92300bd93',
'0x8762db106b2c2a0bccb3a80d1ed41273552616e8',
'0xc011a73ee8576fb46f5e1c5751ca3b9fe0af2a6f',
'0x476c5e26a75bd202a9683ffd34359c0cc15be0ff',
'0x0ae055097c6d159879521c384f1d2123d1f195e6',
'0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6',
'0x57ab1ec28d129707052df4df418d58a2d46d5f51',
'0x6b3595068778dd592e39a122f4f5a5cf09c90fe2',
'0xb8baa0e4287890a5f79863ab62b7f175cecbd433',
'0x8ce9137d39326ad0cd6491fb5cc0cba0e089b6a9',
'0x0ba45a8b5d5575935b8158a88c631e9f9c95a2e5',
'0x05d3606d5c81eb9b7b18530995ec9b29da05faba',
'0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',
'0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
'0xdac17f958d2ee523a2206206994597c13d831ec7',
'0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
'0x0d438f3b5175bebc262bf23753c1e53d03432bde',
'0x41ab1b6fcbb2fa9dced81acbdec13ea6315f2bf2',
'0x0bc529c00c6401aef6d220be8c6ea1667f6ad93e',
'0x04fa0d235c4abf4bcf4787af4cf447de572ef828',
'0x4a220e6096b25eadb88358cb44068a3248254675',
'0xe41d2489571d322189246dafa5ebde1f4699f498',
'0x62359ed7505efc61ff1d56fef82158ccaffa23d7',
'0x2ba592f78db6436527729929aaf6c908497cb200',
'0x429881672b9ae42b8eba0e26cd9c73711b891ca5',
'0xf970b8e36e23f7fc3fd752eea86f8be8d83375a6']

var tokenDecimals = {}
for (var i = 0; i < tokens.length; i++) {
    let taddr = tokens[i]
    let tcontract = new ethers.Contract(taddr, abi, provider);
    let tdecimals
    try{
        tdecimals = await tcontract.decimals()
    } catch (e) {
        tdecimals = "error"
    }
    console.log(taddr, tdecimals)
    tokenDecimals[taddr] = tdecimals
}
console.log(tokenDecimals)



