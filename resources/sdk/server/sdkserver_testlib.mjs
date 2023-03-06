export async function plus(a,b){
    await wait(5000);
    return {func: "plus", a:a, b:b, result: a+b};
}

export async function mul(a,b){
    await wait(5000);
    return {func: "mul", a:a, b:b, result: a*b};
}

function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time))
  }
  
async function wait(maxdelayms) {
    const delayms = Math.floor(Math.random() * maxdelayms) // Generate a random delay time
  
    console.log(`[wait] waiting for ${delayms}ms (maxdelay=${maxdelayms}ms)...`)
    await delay(delayms)
    //console.log(`[wait] done waiting`)
  }
  
export function qmul(a,b){
    return {func: "qmul", a:a, b:b, result: a*b};
}

export function qplus(a,b){
  return {func: "qplus", a:a, b:b, result: a+b};
}


// module.exports = {
//     plus: plus,
//     mul: mul,
//     qplus: qplus,
//     qmul: qmul
//   }