import { ethers } from 'ethers';

// Address of the ERC20 token contract
const tokenAddress = '0x1234567890123456789012345678901234567890';

// ABI of the ERC20 token contract
const tokenAbi = [
  'function balanceOf(address account) view returns (uint256)',
  'function decimals() view returns (uint8)'
];

// set ALCHEMY_RPCURL running `source /Volumes/Private/bin/secrets`
const rpcUrl = process.env.ALCHEMY_RPCURL;
const provider = new ethers.providers.JsonRpcProvider(rpcUrl);
const addr = "0x02aA0c42702110747c4cEa3C4Daf4D6cF701a6Ee"
const contract = new ethers.Contract(contractAddress, tokenAbi, provider);
const decimals = await contract.decimals();
console.log(`Decimals: ${decimals}`);
const balanceOf = await contract.balanceOf(addr);
console.log(`balanceOf: ${balanceOf}`);

