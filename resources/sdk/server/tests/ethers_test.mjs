// run `source /Volumes/Private/bin/secrets` to set the environment variables

// this imports the ethers library, and the JsonRpcProvider class
import { ethers } from "ethers";
import { JsonRpcProvider, parseEther } from 'ethers';

// we set the RPC URLs either from the environment variables or from the default values
// the environment variable can be set by running `source /Volumes/Private/bin/secrets`
const rpcUrl = process.env.ALCHEMYURL;
const rpcUrlBSC = 'https://bsc-dataseed1.binance.org/';
const rpcUrlBSCtest = 'https://data-seed-prebsc-1-s1.binance.org:8545/';
//const rpcUrlTly = rpcUrlTly1;

// we create providers using the RPC URLs
const provider = new JsonRpcProvider(rpcUrl)
const providerBSC = new JsonRpcProvider(rpcUrlBSC)
const providerBSCtest = new JsonRpcProvider(rpcUrlBSCtest)
//const providerTly = new JsonRpcProvider(rpcUrlTly)

// we read and log the latest block number
const blockNumber = await provider.getBlockNumber();
const blockNumberBSC = await providerBSC.getBlockNumber();
const blockNumberBSCtest = await providerBSCtest.getBlockNumber();
//const blockNumberTly = await providerTly.getBlockNumber();
const blockNumberTly = "NA";
console.log(`Latest block number: ${blockNumber}, ${blockNumberBSC}, ${blockNumberBSCtest}, ${blockNumberTly}`);

// now we look at wallets; MMSEED is an environment variable that contains the seed phrase
// you can set it by running `source /Volumes/Private/bin/secrets`
// wallet docs are here https://docs.ethers.org/v6/api/wallet/#Wallet
const seedPhrase = process.env.MMSEED;
const wallet = ethers.Wallet.fromPhrase(seedPhrase);
console.log(wallet.address);
console.log("------------------")

// wallet2 is a random wallet; we prints its seed phrase and address
const wallet2 = ethers.Wallet.createRandom()
const words2 = wallet2.mnemonic.phrase
console.log(words2)
console.log(wallet2.address)
console.log("------------------")

// wallet3 is a throwaway HDWallet derived from a seed phrase
// we first look at the mnemonic which is similar to the seed phrase
const phrase="quiz super pitch label soon flash organ jaguar bridge tooth wrong feed"
const mnemonic = ethers.Mnemonic.fromPhrase(phrase)
console.log(mnemonic)
console.log(mnemonic.computeSeed())
console.log(ethers.Mnemonic.phraseToEntropy(phrase))

// now we create the wallet from the phrase and we derive a number of children
const wallet3 = ethers.HDNodeWallet.fromPhrase(phrase)
console.log(wallet3.address)
console.log(wallet3.deriveChild(1).address)
console.log(wallet3.deriveChild(2).address)
console.log("------------------")

// we now neuter the wallet and print the addresses (which are the same as the original)
const wallet3void = wallet3.neuter()
console.log(wallet3void.address)
console.log(wallet3void.deriveChild(1).address)
console.log(wallet3void.deriveChild(2).address)
console.log("------------------")

// now we look at the extended key, which in this case only contains the public key
// for the neutered wallet but both the public and private keys for the original wallet
const wallet3void_xkey = wallet3void.extendedKey
console.log(wallet3void_xkey)
const wallet3_xkey = wallet3.extendedKey
console.log(wallet3_xkey)
const wallet3check = ethers.HDNodeWallet.fromExtendedKey(wallet3void_xkey)
console.log(wallet3check.address)
console.log(wallet3check.privateKey)
console.log(wallet3.privateKey)
console.log("------------------")

// now are are looking at balances of wallet 1
const balance = await provider.getBalance(wallet.address);
const balanceBSC = await providerBSC.getBalance(wallet.address);
const balanceBSCtest = await providerBSCtest.getBalance(wallet.address);
console.log(`Latest balance Wei: ${balance}, ${balanceBSC}, ${balanceBSCtest}`);
console.log(`Latest balance ETH/BSC: ${ethers.formatEther(balance)}, ${ethers.formatEther(balanceBSC)}, ${ethers.formatEther(balanceBSCtest)}`);
console.log("------------------")

// now we look at transferring some funds (on BSC testnet)
console.log(wallet.address)  // Base account in throwaway MetaMask
// 0x510E4D5dc348A22Fa7BdC13Ba1e8e25449DC3D1b

console.log(wallet3.address) // DONOTUSE2 in throwaway MetaMask
// 0x02aA0c42702110747c4cEa3C4Daf4D6cF701a6Ee

const walletBSCTest = wallet.connect(providerBSCtest)
const wallet3BSCTest = wallet3.connect(providerBSCtest)

// sending 0.01 BNB from wallet to wallet3
var result = await walletBSCTest.sendTransaction({ to: wallet3BSCTest.address, value: parseEther("0.01") })
console.log(result)

// sending 0.01 BNB from wallet3 to wallet
var result = await wallet3BSCTest.sendTransaction({ to: walletBSCTest.address, value: parseEther("0.01") })
console.log(result)




