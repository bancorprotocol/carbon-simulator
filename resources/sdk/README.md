# CarbonSDK Generic API 

_example code for a  generic API for the CarbonSDK library_

**THIS CODE MUST NOT BE USED IN PRODUCTION, IT IS SOLELY PROVIDED AS AN EXAMPLE FOR HOW TO INTERFACE THE CARBON SDK IN ANOTHER ENVIRONMENT THAN NODE. IN PARTICULAR, THIS CODE MUST NEVER BE USED WITH PRIVATE KEYS THAT CONTROL MEANINGFUL FUNDS AS ALL THOSE FUNDS WILL BE AT RISK.**

## Overview

This code consists of three parts

1. an http server that listens on localhost for json-encoded API requests (`server/sdkserver.mjs`) and transmits them to the Node-based Carbon SDK (`server/sdkserver_dispatch.mjs`) 
2. a Python class the wraps the http server, allowing both synchronous and asyncronous access (`carbon/sdk/sdk.py`) and helper functions (`carbon/sdk/sdktoken.py`)
3. a number of testing and example notebooks that shows how to use the API from within Python / Juypyter


## Usage

After having installed the relevant Node libraries, to use the API you must run the following steps

    1. point a terminal to the `server` 
    2. run `source /path/to/set_private_keys` to set the private keys
    3. run `node sdkserver.mjs`
    4. run one of the example notebooks, or your own code
    5. hit Ctrl-C to stop the server when done


## Installation

Clone the Carbon Simulator repo and point a terminal to `/resources/sdk` in the repo. The notebooks `NBXX` in this repo require modules from the `Carbon` library, and it is recommended to use the one from the repo to ensure version compatibility. The easiest way to achieve this on a Mac is

    cd resources/sdk
    ln -s ../../carbon carbon

Also please note that at the time of the writing you may need the `beta` or even the `SDK` branch in the repo to obtain the latest version of the SDK.

Then point a terminal to `/resources/sdk/server` and use your favorite package manager (`npm` or `yarn`) to install the dependedencies in the `package.json` file. Note that the Carbon SDK at the moment can only be installed using yarn.

Finally create a file `/path/to/set_private_keys`, ideally on an encrypted location, that on a Mac using `zsh` must contain the following command setting the pass phrase for the wallet the server will use to sign transactions.

    export SDKSERVER_MEMONICPHRASE="list of twelve words for my insecure wallet..."
    export SDKSERVER_RPCURL="https://rpc.tenderly.co/fork/cbb1..."
    export SDKSERVER_EXPLORER="https://dashboard.tenderly.co/bancor/..."
    export SDKSERVER_UI="https://..."

**IMPORTANT NOTE: DO NOT USE A PASS PHRASE CORRESPONDING TO AN ADDRESS THAT CONTAINS MEANINGFUL AMOUNTS OF FUNDS. ALL THOSE FUNDS ARE AT RISK.**

Note that you do not necessarily need to specify a private key in this way to run the SDK, but at the moment this is the only way to transmit transaction to the blockchain. Having said this, the Python / http API does allow to retrieve the unsigned transaction that can then be signed and submitted to the blockchain via alternative means.





