# Resources

_various Carbon related resources and code_

## Contents

- `benchmark`: benchmark data for reconciliation with the smart contract
- `data`: market data, including code to retrieve it
- `examples`: examples for using the Carbon library
- `NBTest`: the Carbon Simulator test suite; also serves as detailed examples for the various features of the library
- `notes`: various text and presentation content
- `routing`: analysis on optimal routing and arbitrage between Carbon and other AMMs
- `sdk`: example notebooks how to use the SDK
- `sdk/server`: the NodeJS code for wrapping the Carbon SDK into an http server
- `whitepaper`: resources related to the Carbon whitepaper

## Using latest Carbon in resources

To use the latest Carbon code in the resources, run the following command from the root of the repository:

```bash
cp gitignore .gitignore
cd resources
cd NBTest
ln -s ../../carbon carbon
cd ../sdk
ln -s ../../carbon carbon
cd ../demo  
ln -s ../../carbon carbon
cd ../examples
ln -s ../../carbon carbon
cd ../data
ln -s ../../carbon carbon
cd ../..
```

```bash
## Links to other resources

- [carbondefi.xyz][site] CarbonCalculations

- [litepaper][litepaper]

- [whitepaper][whitepaper]

- [mathematical summary][mathsummary]

- [innovation disclosure document][patent]



[site]:https://carbondefi.xyz
[whitepaper]:https://carbondefi.xyz/whitepaper
[litepaper]:https://carbondefi.xyz/litepaper
[patent]:https://carbondefi.xyz/patent
[mathsummary]:https://carbondefi.xyz/mathsummary
[github]:https://github.com/bancorprotocol
[simulator]:https://github.com/bancorprotocol/carbon-simulator