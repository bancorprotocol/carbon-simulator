import { ethers } from 'ethers';


export var wallet
export var signer
export var provider

wallet = ethers.Wallet.createRandom();
console.log(wallet.address);
console.log(wallet.mnemonic);
console.log(wallet.mnemonic.phrase);
//signer = wallet.connect(provider);

// https://etherscan.io/address/0xf977814e90da44bfa03b6295a0616a897441acec
// binance8 address