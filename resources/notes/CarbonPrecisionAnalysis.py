# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
from decimal import *
getcontext().prec = 100
import pandas as pd
import numpy as np
from typing import Tuple, Union, Dict, List, Optional
import pickle
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
import textwrap
from tabulate import tabulate
import re
import copy
from itertools import permutations

# %%
MIN_VALUE = 0
MAX_VALUE = 2**256 - 1

MAX_B_AND_S_BITS = 96
MANTISSA_BITS = 48
EXPONENT_BITS = 6
SCALING_FACTOR = 48

STORAGE_PRECISE = {
    'B' : {
        'value' : []
        },
    'S' : {
        'value' : []
        },
    'y' : {
        'value' : []
        },
    'y_int' : {
        'value' : []
        }
    }

STORAGE_DECIMAL = {
    'B' : {
        'bits' : [],
        'value' : [],
        'mantissa' : [],
        'exponent' : [],
        'reconstituted value': [],
        'reconstitution error' : []
        },
    'S' : {
        'bits' : [],
        'value' : [],
        'mantissa' : [],
        'exponent' : [],
        'reconstituted value': [],
        'reconstitution error' : []
        },
    'y' : {
        'bits' : [],
        'value' : []
        },     
    'y_int' : {
        'bits' : [],
        'value' : []
        } 
    }

STORAGE_BINARY = {
    'B' : {
        'bits' : [],
        'value' : [],
        'mantissa' : [],
        'exponent' : [],
        'reconstituted value': [],
        'reconstitution error' : []
        },
    'S' : {
        'bits' : [],
        'value' : [],
        'mantissa' : [],
        'exponent' : [],
        'reconstituted value': [],
        'reconstitution error' : [] 
        },
    'y' : {
        'bits' : [],
        'value' : []
        },     
    'y_int' : {
        'bits' : [],
        'value' : []
        } 
    }

STORAGE = {
    'precise' : STORAGE_PRECISE,
    'decimal' : STORAGE_DECIMAL,
    'binary' : STORAGE_BINARY
    }


# %%
def get_maximum_mantissa_binary(
    ) -> str:
    """
    ### Returns a string representing the maximum mantissa in binary format.

    ## Parameters:
    None
    
    ## Returns:
    | Return names          | Type   | Return Descriptions                                               |
    |:----------------------|:-------|:------------------------------------------------------------------|
    | `max_mantissa_binary` | `str`  | A string representation of the maximum mantissa in binary format. |
        
    ## Example:
    >>> global MANTISSA_BITS = 48
    >>> get_maximum_mantissa_binary():
    '111111111111111111111111111111111111111111111111'
    """
    global MANTISSA_BITS
    max_mantissa_binary = '1'*MANTISSA_BITS
    return(max_mantissa_binary)


# %%
def get_maximum_mantissa_decimal(
    max_mantissa_binary: str
    ) -> int:
    """
    ### Returns the maximum mantissa in decimal format from the provided binary representation.

    ## Parameters:
    | Parameter names       | Type   | Parameter Descriptions                                            |
    |:----------------------|:-------|:------------------------------------------------------------------|
    | `max_mantissa_binary` | `str`  | A string representation of the maximum mantissa in binary format. |

    ## Returns:
    | Return names           | Type   | Return Descriptions                     |
    |:-----------------------|:-------|:----------------------------------------|
    | `max_mantissa_decimal` | `int`  | The maximum mantissa in decimal format. |
    
    ## Example:
    >>> global MANTISSA_BITS = 48
    >>> calculate_maximum_mantissa_decimal(get_maximum_mantissa_binary())
    1099511627775
    """
    max_mantissa_decimal = int(max_mantissa_binary, 2)
    return(max_mantissa_decimal)


# %%
def calculate_maximum_exponent_decimal(
    ) -> int:
    """
    ### Calculates and returns the maximum exponent in decimal format.
    
    ## Parameters:
    None

    ## Returns:
    | Return names           | Type   | Return Descriptions                     |
    |:-----------------------|:-------|:----------------------------------------|
    | `max_exponent_decimal` | `int`  | The maximum exponent in decimal format. |

    ## Example:
    >>> global MAX_B_AND_S_BITS = 96
    >>> global MANTISSA_BITS = 48
    >>> calculate_maximum_exponent_decimal()
    48
    """
    global MANTISSA_BITS 
    global MAX_B_AND_S_BITS
    max_exponent_decimal = MAX_B_AND_S_BITS - MANTISSA_BITS
    return(max_exponent_decimal)


# %%
def get_maximum_exponent_binary(
    max_exponent_decimal: int
    ) -> str:
    """
    ### Returns a string representing the maximum exponent in binary format.

    ## Parameters:
    | Parameter names        | Type   | Parameter Descriptions                  |
    |:-----------------------|:-------|:----------------------------------------|
    | `max_exponent_decimal` | `int`  | The maximum exponent in decimal format. |

    ## Returns:
    | Return names          | Type   | Return Descriptions                                               |
    |:----------------------|:-------|:------------------------------------------------------------------|
    | `max_exponent_binary` | `str`  | A string representation of the maximum exponent in binary format. |

    ## Example:
    >>> global MAX_B_AND_S_BITS = 96
    >>> global MANTISSA_BITS = 48
    >>> get_maximum_exponent_binary(calculate_maximum_exponent_decimal()) 
    '110000'
    """
    max_exponent_binary = bin(int(max_exponent_decimal))[2:]
    return(max_exponent_binary)


# %%
def calculate_maximum_B_or_S_value_decimal(
    max_mantissa_decimal: int, 
    max_exponent_decimal: int
    ) -> int:
    """
    ### Calculates and returns the maximum B value in decimal format from the provided mantissa and exponent.

    ## Parameters:
    | Parameter names        | Type   | Parameter Descriptions                  |
    |:-----------------------|:-------|:----------------------------------------|
    | `max_mantissa_decimal` | `int`  | The maximum mantissa in decimal format. |
    | `max_exponent_decimal` | `int`  | The maximum exponent in decimal format. |

    ## Returns:
    | Return names          | Type   | Return Descriptions                    |
    |:----------------------|:-------|:---------------------------------------|
    | `max_B_value_decimal` | `int`  | The maximum B value in decimal format. |

    ## Example:
    >>> global MAX_B_AND_S_BITS = 96
    >>> global MANTISSA_BITS = 48
    >>> calculate_maximum_B_or_S_value_decimal(calculate_maximum_mantissa_decimal(get_maximum_mantissa_binary()),
                                               calculate_maximum_exponent_decimal())
    79228162514264056118567239680
    """
    max_B_value_decimal = max_mantissa_decimal*2**max_exponent_decimal
    return(max_B_value_decimal)


# %%
def calculate_maximum_B_or_S_value_binary(
    ) -> str:
    """
    ### Returns a string representing the maximum B value in binary format.
    
    ## Parameters:
    None

    ## Returns:
    | Return names         | Type   | Return Descriptions                                              |
    |:---------------------|:-------|:-----------------------------------------------------------------|
    | `max_B_value_binary` | `str`  | A string representation of the maximum B value in binary format. |
    
    ## Example:
    >>> global MANTISSA_BITS = 48
    >>> global MAX_B_AND_S_BITS = 96
    >>> calculate_maximum_B_or_S_value_binary()
    '111111111111111111111111111111111111111111111111000000000000000000000000000000000000000000000000'
    """
    global MANTISSA_BITS 
    global MAX_B_AND_S_BITS
    mantissa_part = '1'*MANTISSA_BITS 
    exponent_part = '0'*(MAX_B_AND_S_BITS - MANTISSA_BITS)
    max_B_value_binary = mantissa_part + exponent_part
    return(max_B_value_binary)


# %%
def calculate_maximum_pb_value_decimal(
    ) -> int:
    """
    ### Calculates the maximum `P_b` value in decimal format from the provided mantissa and exponent.
    
    ## Parameters:
    None

    ## Returns:
    | Return names           | Type   | Return Descriptions                        |
    |:-----------------------|:-------|:-------------------------------------------|
    | `max_pb_value_decimal` | `int`  | The maximum `P_b` value in decimal format. |
    
    ## Example:
    >>> global SCALING_FACTOR = 48
    >>> global MANTISSA_BITS = 48
    >>> calculate_maximum_pb_value_decimal()
    79228162514263774643590529025
    """
    global SCALING_FACTOR
    global MANTISSA_BITS
    max_pb_value_decimal = 2**(2*(MANTISSA_BITS - SCALING_FACTOR))*(2**MANTISSA_BITS - 1)**2
    return(max_pb_value_decimal)


# %%
def get_maximum_pb_value_binary(
    max_pb_value_decimal: int
    ) -> str:
    """
    ### Returns a string representing the maximum `P_b` value in binary format.

    ## Parameters:
    | Parameter names        | Type   | Parameter Descriptions                     |
    |:-----------------------|:-------|:-------------------------------------------|
    | `max_pb_value_decimal` | `int`  | The maximum `P_b` value in decimal format. |

    ## Returns:
    | Return names          | Type   | Return Descriptions                                                |
    |:----------------------|:-------|:-------------------------------------------------------------------|
    | `max_pb_value_binary` | `str`  | A string representation of the maximum P_b value in binary format. |

    ## Example:
    >>> global SCALING_FACTOR = 48
    >>> global MANTISSA_BITS = 48
    >>> get_maximum_exponent_binary(calculate_maximum_exponent_decimal()) 
    '110000'
    """
    max_pb_value_binary = bin(int(max_pb_value_decimal))[2:]
    return(max_pb_value_binary)


# %%
def get_price_input_thresholds(
    ) -> Dict[str, Union[str, int]]:
    """
    ### calculates the maximum `mantissa`, `exponent`, and `P_b` value in binary and decimal formats and returns a dictionary of the results.

    ## Parameters:
    None
    
    ## Returns:
    | Return names   | Type   | Return Descriptions                                    |
    |:---------------|:-------|:-------------------------------------------------------|
    | `output_dict`  | dict   | A dictionary containing the following key-value pairs: |
    
    ## Returned Dictionary:
    | Key                     | Key Type   | Value                                      | Value Type   |
    |:------------------------|:-----------|:-------------------------------------------|:-------------|
    | max mantissa (binary)   | `str`      | The maximum mantissa in binary format.     | `str`        |
    | max exponent (binary)   | `str`      | The maximum exponent in binary format.     | `str`        |
    | max B value (binary)    | `str`      | The maximum `B` value in binary format.    | `str`        |
    | max mantissa (decimal)  | `str`      | The maximum mantissa in decimal format.    | `int`        |
    | max exponent (decimal)  | `str`      | The maximum exponent in decimal format.    | `int`        |
    | max B value (decimal)   | `str`      | The maximum `B` value in decimal format.   | `int`        |
    | max P_b value (decimal) | `str`      | The maximum `P_b` value in decimal format. | `int`        |
    
    ## Uses the following functions:
    | Function                                 | Type       | Description                                                |
    |:-----------------------------------------|:-----------|:-----------------------------------------------------------|
    | `get_maximum_mantissa_binary`            | `function` | Calculates the maximum mantissa in binary format.          |
    | `get_maximum_mantissa_decimal`           | `function` | Calculates the maximum mantissa in decimal format.         |
    | `calculate_maximum_exponent_decimal`     | `function` | Calculates the maximum exponent in decimal format.         |
    | `get_maximum_exponent_binary`            | `function` | Calculates the maximum exponent in binary format.          |
    | `calculate_maximum_B_or_S_value_decimal` | `function` | Calculates the maximum `B` or `S` value in decimal format. |
    | `calculate_maximum_B_or_S_value_binary`  | `function` | Calculates the maximum `B` or `S` value in binary format.  |
    | `calculate_maximum_pb_value_decimal`     | `function` | Calculates the maximum `P_b` value in decimal format.      |
    
    ## Example:
    >>> global SCALING_FACTOR = 48
    >>> global MANTISSA_BITS = 48
    >>> global EXPONENT_BITS = 6
    >>> global MAX_B_AND_S_BITS = 96
    >>> get_price_input_thresholds()
                        Key    Value
    -----------------------    ------------------------------------------------------------------------------------------------
      'max mantissa (binary)'  111111111111111111111111111111111111111111111111
      'max exponent (binary)'  110000
       'max B value (binary)'  111111111111111111111111111111111111111111111111000000000000000000000000000000000000000000000000
     'max mantissa (decimal)'  281474976710655
     'max exponent (decimal)'  48
      'max B value (decimal)'  79228162514264056118567239680
    'max P_b value (decimal)'  79228162514263774643590529025
    """
    global SCALING_FACTOR
    global MANTISSA_BITS
    global EXPONENT_BITS
    global MAX_B_AND_S_BITS
    max_mantissa_binary = get_maximum_mantissa_binary()
    max_mantissa_decimal = get_maximum_mantissa_decimal(max_mantissa_binary)
    max_exponent_decimal = calculate_maximum_exponent_decimal()
    max_exponent_binary = get_maximum_exponent_binary(max_exponent_decimal)
    max_B_or_S_value_decimal = calculate_maximum_B_or_S_value_decimal(max_mantissa_decimal, max_exponent_decimal)
    max_B_or_S_value_binary = calculate_maximum_B_or_S_value_binary()
    max_pb_value_decimal = calculate_maximum_pb_value_decimal()
    output_names = ['max mantissa (binary)', 'max exponent (binary)', 'max B value (binary)', 'max mantissa (decimal)', 'max exponent (decimal)', 'max B value (decimal)', 'max P_b value (decimal)']
    output_values = [max_mantissa_binary, max_exponent_binary, max_B_or_S_value_binary, max_mantissa_decimal, max_exponent_decimal, max_B_or_S_value_decimal, max_pb_value_decimal]
    output_dict = dict(zip(output_names, output_values))
    table = [(k, v) for k, v in output_dict.items()]
    print(tabulate(table, headers=['Key', 'Value'], tablefmt = 'simple', colalign=('right', 'left')))
    return(output_dict)


# %%
def calculate_P_b_from_scaled_up_B(
    B: int
    ) -> Decimal:
    """
    ### Calculates the precise value of `P_b`, given the scaled-up value of `B`.

    ## Parameters:
    | Parameter names   | Type   | Description                         |
    |:------------------|:-------|:------------------------------------|
    | `B`               | `int`  | The scaled-up integer value of `B`. |

    ## Returns:
    | Return names   | Type      | Description                |
    |:---------------|:----------|:---------------------------|
    | `P_b`          | `Decimal` | The precise value of `P_a`.|
    
    ## Example:
    >>> global SCALING_FACTOR = 48
    >>> B_scaled_up = 123456789123456789
    >>> calculate_P_b_from_scaled_up_B(B_scaled_up)
    Decimal('192375.7701427136541944783905952941026475848705036394707988201338566547349273605505004525184631347656')
    """
    global SCALING_FACTOR
    P_b = (Decimal(B)/Decimal('2')**Decimal(SCALING_FACTOR))**Decimal('2')
    return(P_b) 


# %%
def calculate_P_a_from_B_scaled_up_and_S_scaled_up(
    B: int, 
    S: int
    ) -> Decimal:
    """
    ### Calculates the precise value of `P_a`, given the values of `B` and `S`.

    ## Parameters:
    | Parameter names   | Type   | Description                         |
    |:------------------|:-------|:------------------------------------|
    | `B`               | `int`  | The scaled-up integer value of `B`. |
    | `S`               | `int`  | The scaled-up integer value of `S`. |

    ## Returns:
    | Return names   | Type      | Description                 |
    |:---------------|:----------|:----------------------------|
    | `P_a`          | `Decimal` | The precise value of `P_a`. |
    
    ## Example:
    >>> global SCALING_FACTOR = 48
    >>> B_scaled_up = 123456789123456789
    >>> S_scaled_up = 123456789123456789
    >>> calculate_P_a_from_B_scaled_up_and_S_scaled_up(B_scaled_up, S_scaled_up)
    Decimal('769503.0805708546167779135623811764105903394820145578831952805354266189397094422020018100738525390625')
    """
    global SCALING_FACTOR
    P_a = ((Decimal(S) + Decimal(B))/Decimal('2')**Decimal(SCALING_FACTOR))**Decimal('2')
    return(P_a)


# %%
def write_to_storage(
    B_value: Union[str, int, Decimal],
    S_value: Union[str, int, Decimal],
    y_value: Union[str, int, Decimal],
    y_int_value: Union[str, int],
    B_number_of_bits: Union[str, int, None] = None,
    B_mantissa: Union[str, int, None] = None,
    B_exponent: Union[str, int, None] = None,
    B_reconstituted: Union[str, int, None] = None,
    B_reconstitution_error: Union[str, int, None] = None,
    S_number_of_bits: Union[str, int, None] = None,
    S_mantissa: Union[str, int, None] = None,
    S_exponent: Union[str, int, None] = None,
    S_reconstituted: Union[str, int, None] = None,
    S_reconstitution_error: Union[str, int, None] = None,
    y_number_of_bits: Union[str, int, None] = None,
    y_int_number_of_bits: Union[str, int, None] = None,
    storage_type: str = 'decimal',
    ) -> None:
    """
    ### Writes values to a global storage dictionary for the specified storage type.

    ## Parameters:
    | Parameter names          | Type                       | Description                                                                |
    |:-------------------------|:---------------------------|:---------------------------------------------------------------------------|
    | `B_value`                | `Union[str, int, Decimal]` | The `B` value of the curve (refer to the Carbon whitepaper).               |
    | `S_value`                | `Union[str, int, Decimal]` | The `S` value (refer to the Carbon whitepaper).                            |
    | `y_value`                | `Union[str, int, Decimal]` | The `y` value (refer to the Carbon whitepaper).                            |
    | `y_int_value`            | `Union[str, int]`          | The `y` intercept value (refer to the Carbon whitepaper).                  |
    | `B_number_of_bits`       | `Union[str, int, None]`    | The total bits used to represent the reconstituted `B` value.              |
    | `B_mantissa`             | `Union[str, int, None]`    | The mantissa of the compressed `B` value.                                  |
    | `B_exponent`             | `Union[str, int, None]`    | The exponent of the compressed `B` value.                                  |
    | `B_reconstituted`        | `Union[str, int, None]`    | The reconstituted value of `B` (i.e `mantissa*2**exponent`).               |
    | `B_reconstitution_error` | `Union[str, int, None]`    | The reconstitution error of `B` (i.e. precision loss after decompression). |
    | `S_number_of_bits`       | `Union[str, int, None]`    | The total bits used to represent the reconstituted `S` value.              |
    | `S_mantissa`             | `Union[str, int, None]`    | The mantissa of the compressed `S` value.                                  |
    | `S_exponent`             | `Union[str, int, None]`    | The exponent of the compressed `S` value.                                  |
    | `S_reconstituted`        | `Union[str, int, None]`    | The reconstituted value of `S` (i.e `mantissa*2**exponent`).               |
    | `S_reconstitution_error` | `Union[str, int, None]`    | The reconstitution error of `S` (i.e. precision loss after decompression). |
    | `y_number_of_bits`       | `Union[str, int, None]`    | The total bits used to represent the `y` value.                            |
    | `y_int_number_of_bits`   | `Union[str, int, None]`    | The number of bits used to represent the the `y` intercept value.          |
    | `storage_type`           | `str`                      | The type of storage to write to. Defaults to 'decimal'.                    |

    ## Returns:
    None
    """
    global STORAGE
    STORAGE[storage_type]['B']['value'] = [B_value]
    STORAGE[storage_type]['S']['value'] = [S_value]
    STORAGE[storage_type]['y']['value'] = [y_value]
    STORAGE[storage_type]['y_int']['value'] = [y_int_value]
    if storage_type != 'precise':
        STORAGE[storage_type]['B']['bits'] = [B_number_of_bits]
        STORAGE[storage_type]['B']['mantissa'] = [B_mantissa]
        STORAGE[storage_type]['B']['exponent'] = [B_exponent]
        STORAGE[storage_type]['B']['reconstituted value'] = [B_reconstituted]
        STORAGE[storage_type]['B']['reconstitution error'] = [B_reconstitution_error]
        STORAGE[storage_type]['S']['bits'] = [S_number_of_bits]
        STORAGE[storage_type]['S']['mantissa'] = [S_mantissa]
        STORAGE[storage_type]['S']['exponent'] = [S_exponent]
        STORAGE[storage_type]['S']['reconstituted value'] = [S_reconstituted]
        STORAGE[storage_type]['S']['reconstitution error'] = [S_reconstitution_error]
        STORAGE[storage_type]['y']['bits'] = [y_number_of_bits]
        STORAGE[storage_type]['y_int']['bits'] = [y_int_number_of_bits]
    return(None)


# %%
def bitshift(
    number: int
    ) -> Tuple[Union[int, str]]:
    """
    ### Takes in an integer value and returns the number of bits, mantissa, and exponent in binary and decimal format.

    ## Parameters:
    | Parameter names   | Type   | Description                        |
    |:------------------|:-------|:-----------------------------------|
    | `number`          | `int`  | The integer value to be processed. |

    ## Returns:
    | Return names       | Type                     | Return Descriptions                                                                                                                            |
    |:-------------------|:-------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------|
    | `number_of_bits`   | `int`                    | The number of bits of the input value.                                                                                                         |
    | `mantissa_decimal` | `int`                    | The decimal representation of the mantissa of the input value.                                                                                 |
    | `exponent_decimal` | `int`                    | The decimal representation of the exponent of the input value.                                                                                 |
    | `binary_number`    | `str`                    | The binary representation of the input value.                                                                                                  |
    | `mantissa_binary`  | `str`                    | The binary representation of the mantissa of the input value.                                                                                  |
    | `exponent_binary`  | `str`                    | The binary representation of the exponent of the input value.                                                                                  |
    |                    | `Tuple[Union[int, str]]` | A tuple of `number_of_bits`, `mantissa_decimal`, `exponent_decimal`, `binary_number`, `mantissa_binary`, and `exponent_binary`, in that order. |
    
    ## Example:
    >>> global MANTISSA_BITS = 48
    >>> number = 123456789123456789123456789
    >>> bitshift(number)
    (87,
    224566591211363,
    39,
    '110011000011110111111011111001011100011101100011001111101111100000001000101111100010101',
    '110011000011110111111011111001011100011101100011',
    '100111')
    """
    global MANTISSA_BITS
    binary_number = bin(int(number))[2:]
    number_of_bits = len(binary_number)
    mantissa_binary = binary_number[:MANTISSA_BITS]
    mantissa_decimal = int(mantissa_binary, 2)
    exponent_decimal = number_of_bits - len(mantissa_binary)
    exponent_binary = bin(int(exponent_decimal))[2:]
    return(number_of_bits, 
           mantissa_decimal, 
           exponent_decimal, 
           binary_number, 
           mantissa_binary, 
           exponent_binary)


# %%
def process_user_inputs_binary(
    S_processed_decimal: int,
    B_processed_decimal: int,
    y_processed_decimal: int,
    y_int_processed_decimal: int,
    ) -> Tuple[Union[int, str]]:
    """
    ###  Processes the input values for `S`, `B`, `y`, and `y_int`, and returns the compressed forms of `B` and `S` in terms of their `mantissa`, and `exponent` values, and the number of bits each storage item occupies.

    ## Parameters:
    | Parameter names           | Type   | Description                                      |
    |:--------------------------|:-------|:-------------------------------------------------|
    | `S_processed_decimal`     | `int`  | The decimal representation of the `S` value.     |
    | `B_processed_decimal`     | `int`  | The decimal representation of the `B` value.     |
    | `y_processed_decimal`     | `int`  | The decimal representation of the `y` value.     |
    | `y_int_processed_decimal` | `int`  | The decimal representation of the `y_int` value. |

    ## Returns:
    | Return names             | Type                     | Description                                                                                                                                                                                                                                                                                                                                                                         |
    |:-------------------------|:-------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `S_number_of_bits`       | `int`                    | The number of bits of the `S` value, after multiplying by `2**exponent`.                                                                                                                                                                                                                                                                                                            |
    | `S_mantissa_decimal`     | `int`                    | The decimal mantissa of the `S` value.                                                                                                                                                                                                                                                                                                                                              |
    | `S_exponent_decimal`     | `int`                    | The decimal exponent of the `S` value.                                                                                                                                                                                                                                                                                                                                              |
    | `B_number_of_bits`       | `int`                    | The number of bits of the `B` value, after multiplying by `2**exponent`.                                                                                                                                                                                                                                                                                                            |
    | `B_mantissa_decimal`     | `int`                    | The decimal mantissa of the `B` value.                                                                                                                                                                                                                                                                                                                                              |
    | `B_exponent_decimal`     | `int`                    | The decimal exponent of the `B` value.                                                                                                                                                                                                                                                                                                                                              |
    | `S_number_binary`        | `str`                    | The binary representation of the `S` value.                                                                                                                                                                                                                                                                                                                                         |
    | `S_mantissa_binary`      | `str`                    | The binary mantissa of the `S` value.                                                                                                                                                                                                                                                                                                                                               |
    | `S_exponent_binary`      | `str`                    | The binary exponent of the `S` value.                                                                                                                                                                                                                                                                                                                                               |
    | `B_number_binary`        | `str`                    | The binary representation of the `B` value.                                                                                                                                                                                                                                                                                                                                         |
    | `B_mantissa_binary`      | `str`                    | The binary mantissa of the `B` value.                                                                                                                                                                                                                                                                                                                                               |
    | `B_exponent_binary`      | `str`                    | The binary exponent of the `B` value.                                                                                                                                                                                                                                                                                                                                               |
    | `y_number_of_bits`       | `int`                    | The number of bits used to store the value of `y`.                                                                                                                                                                                                                                                                                                                                  |
    | `y_processed_binary`     | `str`                    | The binary representation of the processed `y` value.                                                                                                                                                                                                                                                                                                                               |
    | `y_int_number_of_bits`   | `int`                    | The number of bits used to store the value of `y_int`.                                                                                                                                                                                                                                                                                                                              |
    | `y_int_processed_binary` | `str`                    | The binary representation of the processed `y_int` value.                                                                                                                                                                                                                                                                                                                           |
    |                          | `Tuple[Union[int, str]]` | A tuple of `S_number_of_bits`, `S_mantissa_decimal`, `S_exponent_decimal`, `B_number_of_bits`, `B_mantissa_decimal`, `B_exponent_decimal`, `S_number_binary`, `S_mantissa_binary`, `S_exponent_binary`, `B_number_binary`, `B_mantissa_binary`, `B_exponent_binary`, `y_number_of_bits`, `y_processed_binary`, `y_int_number_of_bits`, and `y_int_processed_binary`, in that order. |   
    
    ## Example:
    >>> global MANTISSA_BITS = 48
    >>> S_processed_decimal = 123456789123456789
    >>> B_processed_decimal = 123456789123456789
    >>> y_processed_decimal = 123123123
    >>> y_int_processed_decimal = 321321321
    >>> process_user_inputs_binary(S_processed_decimal,
                                   B_processed_decimal,
                                   y_processed_decimal,
                                   y_int_processed_decimal)
    ( 57, 
      241126541256751, 
      9, 
      57, 
      241126541256751, 
      9,
     '110110110100110110100101110101100110100000101111100010101',
     '110110110100110110100101110101100110100000101111',
     '1001',
     '110110110100110110100101110101100110100000101111100010101',
     '110110110100110110100101110101100110100000101111',
     '1001',
      27, 
     '111010101101011010110110011',
      29, 
     '10011001001101111100101101001')
    
    ## Uses the following functions:
    | Function   | Type       | Description                                                                                                        |
    |:-----------|:-----------|:-------------------------------------------------------------------------------------------------------------------|
    | `bitshift` | `function` | Takes in an integer value and returns the number of bits, `mantissa`, and `exponent` in binary and decimal format. |
    
    """
    (S_number_of_bits,
     S_mantissa_decimal,
     S_exponent_decimal,
     S_number_binary,
     S_mantissa_binary,
     S_exponent_binary) = bitshift(S_processed_decimal)
    (B_number_of_bits,
     B_mantissa_decimal,
     B_exponent_decimal,
     B_number_binary,
     B_mantissa_binary,
     B_exponent_binary) = bitshift(B_processed_decimal)
    y_processed_binary = bin(int(y_processed_decimal))[2:]
    y_number_of_bits = len(y_processed_binary)
    y_int_processed_binary = bin(int(y_int_processed_decimal))[2:]
    y_int_number_of_bits = len(y_int_processed_binary)
    return(S_number_of_bits, 
           S_mantissa_decimal, 
           S_exponent_decimal, 
           B_number_of_bits, 
           B_mantissa_decimal, 
           B_exponent_decimal, 
           S_number_binary, 
           S_mantissa_binary, 
           S_exponent_binary, 
           B_number_binary, 
           B_mantissa_binary, 
           B_exponent_binary, 
           y_number_of_bits, 
           y_processed_binary, 
           y_int_number_of_bits, 
           y_int_processed_binary)


# %%
def process_user_inputs(
    P_a: Decimal, 
    P_b: Decimal, 
    output_type: str
    ) -> Union[Tuple[Decimal], Tuple[int]]:
    """
    ### Calculates the values of `S` and `B` from the user inputs `P_a` and `P_b`.

    ## Parameters:
    | Parameter names   | Type      | Description                                             |
    |:------------------|:----------|:--------------------------------------------------------|
    | `P_a`             | `Decimal` | The precise value of `P_a`, as input by the user.       |
    | `P_b`             | `Decimal` | The precise value of `P_b`, as input by the user.       |
    | `output_type`     | `str`     | The desired output type, either 'precise' or 'decimal'. |

    ## Returns:
    | Return names   | Type                                | Return Descriptions                                                                                                                                                                                                     |
    |:---------------|:------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `B`            | `Union[Decimal, int]`               | The calculated `B` value, either as a precise value (`Decimal`) or just the integer part (`int`), depending on `output_type`.                                                                                           |
    | `S`            | `Union[Decimal, int]`               | The calculated `S` value, either as a precise value (`Decimal`) or just the integer part (`int`), depending on `output_type`.                                                                                           |
    |                | `Union[Tuple[Decimal], Tuple[int]]` | If output_type is "precise", returns a tuple of `Decimal` values (`B_precise`, `S_precise`, in that order). If `output_type` is "decimal", returns a `tuple` of `int` values (`B_decimal`, `S_decimal`, in that order). |
    
    ## Raises:
    | Error Type   | Error Text                         |
    |:-------------|:-----------------------------------|
    | `ValueError` | Invalid output_type: `output_type` |
    
    
    ## Example:
    >>> global SCALING_FACTOR = 48
    >>> P_a = Decimal('654321.654321')
    >>> P_b = Decimal('123456.12346')
    >>> process_user_inputs(P_a, P_b,'decimal')
    (98899958609040691, 128785575330088783)
    >>> process_user_inputs(P_a, P_b, 'precise')
    (Decimal('351.3632357831422294177822111959803856546350870837356514235300327785270288016360504639870911244315083'),
     Decimal('457.5382751073987582031561830018025123796745535032190196370161459611751090788069338752040507846427126'))
    """
    global SCALING_FACTOR
    B = Decimal.sqrt(P_b)
    S = Decimal.sqrt(P_a) - Decimal.sqrt(P_b)
    if output_type == "decimal":
        B = int(((B)*(2**SCALING_FACTOR)))
        S = int(((S)*(2**SCALING_FACTOR)))
    elif output_type != 'precise':
        raise ValueError(f"Invalid output_type: {output_type}")
    return(B, S)


# %%
def get_user_inputs(
    user_inputs: dict
    ) -> Tuple[Union[Decimal, int]]:
    """
    ### Retrieves values from the input dictionary and returns them as a tuple.

    ## Parameters:
    | Parameter name   | Type   | Description                                                                                                       |
    |:-----------------|:-------|:------------------------------------------------------------------------------------------------------------------|
    | `user_inputs`    | `dict` | A dictionary containing the user inputs for the bonding curve. The following keys are expected in the dictionary: |
    
    ## Parameters Dictionary:
    | Key   | Key Type   | Value                                                 | Value Type   |
    |:------|:-----------|:------------------------------------------------------|:-------------|
    | P_a   | `str`      | The highest dy/dx value for the user's bonding curve. | `Decimal`    |
    | P_b   | `str`      | The lowest dy/dx value for the user's bonding curve.  | `Decimal`    |
    | y     | `int`      | The token balance of the user's bonding curve.        | `int`        |
    | y_int | `int`      | The token capacity of the user's bonding curve.       | `int`        |

    ## Returns:
    | Return name   | Return type                  | Return description                                                           |
    |:--------------|:-----------------------------|:-----------------------------------------------------------------------------|
    | `P_a`         | `Decimal`                    | The highest dy/dx value for the user's bonding curve.                        |
    | `P_b`         | `Decimal`                    | The lowest dy/dx value for the user's bonding curve.                         |
    | `y`           | `int`                        | The token balance of the user's bonding curve.                               |
    | `y_int`       | `int`                        | The token capacity of the user's bonding curve.                              |
    |               | `Tuple[Union[Decimal, int]]` | A tuple containing the values for `P_a`, `P_b`, `y`, `y_int`, in that order. |
    """
    P_a = user_inputs['P_a']
    P_b = user_inputs['P_b']
    y = user_inputs['y']
    y_int = user_inputs['y_int']
    return(P_a, P_b, y, y_int)


# %%
def measure_error(
    expected_result: Union[int, Decimal, str], 
    obtained_result: Union[int, Decimal, str], 
    ) -> Union[int, Decimal, str]:

    """
    ### Calculates the relative error between the expected and obtained results. 

    ## Parameters:
    | Parameter name    | Type                       | Description         |
    |:------------------|:---------------------------|:--------------------|
    | `expected_result` | `Union[int, Decimal, str]` | The expected value. |
    | `obtained_result` | `Union[int, Decimal, str]` | The obtained value. |

    ## Returns:
    | Return name   | Type                       | Description                                                                                                                                                                                                                                                                                                                       |
    |:--------------|:---------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `error`       | `Union[int, Decimal, str]` | The relative error between the expected and obtained values. If the `expected_result` is equal to the `obtained_result`, returns 0. `Else` if any of the input values is a string, returns 'N/A'. Else if the expected_result is 0, returns 'infinity'. Otherwise, returns `(obtained_result - expected_result)/expected_result`. |                                                                                                                                                                                                                                                                                                       |
    
    ## Example:
    >>> measure_error('123456', 123455), 
    -8.100051840331778e-06
    >>> measure_error('SolidityOverFlow', 123455)
    'N/A'
    """
    if expected_result == obtained_result:
        error = 0
    elif any(isinstance(i, str) for i in [expected_result, obtained_result]):
        error = 'N/A'
    elif expected_result == 0:
        error = 'infinity'
    else:
        error = (obtained_result - expected_result)/expected_result
    return(error)


# %%
def reconstitute_number(
    mantissa: Union[str, int], 
    exponent: Union[str, int],
    value: Union[str, int], 
    storage_type: str = 'decimal',
    get_error: bool = False
    ) -> Union[str, int, Tuple[Union[str, int], Optional[Union[int, Decimal]]]]:
    """
    ### Reconstitutes a number from its mantissa and exponent.
    
    ## Parameters:
    | Parameter name   | Type              | Description                                                                                                               |
    |:-----------------|:------------------|:--------------------------------------------------------------------------------------------------------------------------|
    | `mantissa`       | `Union[str, int]` | The `mantissa` of the number to be reconstituted.                                                                         |
    | `exponent`       | `Union[str, int]` | The `exponent` of the number to be reconstituted.                                                                         |
    | `value`          | `Union[str, int]` | The expected value of the reconstituted number.                                                                           |
    | `storage_type`   | `str`             | The format in which the `mantissa` and `exponent` are stored (either decimal or binary).                                  |
    | `get_error`      | `bool`            | A boolean that dictates whether or not the relative error associated with reconstitution of the stored value is returned. |
    
    ## Returns:
    | Return name            | Type              | Description                                                                     |
    |:-----------------------|:------------------|:--------------------------------------------------------------------------------|
    | `reconstituted_number` | `Union[str, int]` | The reconstituted number.                                                       |
    | `reconstitution_error` | `float`           | The relative error between the uncompressed value, and its reconstituted value. |

    ## Example:
    >>> reconstitute_number(mantissa = 224566591211363
                            exponent = 39,
                            value = 123456789123456789123456789, 
                            storage_type = 'decimal',
                            get_error = True)
    (123456789123456653898809344, 
    -1.0953196531765891e-15)

    >>> reconstitute_number(mantissa = '110011000011110111111011111001011100011101100011',
                            exponent = '100111',
                            value = '110011000011110111111011111001011100011101100011001111101111100000001000101111100010101', 
                            storage_type = 'binary',
                            get_error = True)
    ('110011000011110111111011111001011100011101100011000000000000000000000000000000000000000',
     -1.0953196531765891e-15)
 
    ## Notes:
    - If `get_error` is `True`, the function returns a tuple containing the reconstituted number and its relative error with respect to the expected value. 
    - If `get_error` is `False`, the function only returns the reconstituted number. 
    - The relative error is computed as the difference between the expected value and the reconstituted value, divided by the expected value.
    
    ## Uses the following functions:
    | Function        | Type       | Description                                                            |
    |:----------------|:-----------|:-----------------------------------------------------------------------|
    | `measure_error` | `function` | Measure the error between a precise number and a reconstituted number. |
    """
    if storage_type == 'decimal':
        reconstituted_number = mantissa*2**exponent
        reconstitution_error = measure_error(value, reconstituted_number)
    elif storage_type == 'binary':
        reconstituted_number = bin(int(int(mantissa, 2)*2**int(exponent, 2)))[2:]
        reconstitution_error = measure_error(int(value, 2), int(reconstituted_number, 2))
    return((reconstituted_number, reconstitution_error) if get_error else reconstituted_number)


# %%
def process_user_inputs_and_write_to_storage(
    user_inputs: Dict[str, Union[Decimal, int]],
    return_error_profile: bool = False
    ) -> Optional[List[Union[Decimal, int, float]]]:
    """
    ### Processes the user inputs and writes the results to the global storage variables.

    ## Parameters:
    | Parameter              | Type                             | Description                                                                                                      |
    |:-----------------------|:---------------------------------|:-----------------------------------------------------------------------------------------------------------------|
    | `user_inputs`          | `Dict[str, Union[int, Decimal]]` | A dictionary containing the input parameters for the error profile analysis, with the following key-value pairs: |
    | `return_error_profile` | `bool`                           | A boolean indicating whether to return the error profile of the process or not. Defaults to `False`.             |
    
    ## Parameters Dictionary:
    | Key   | Key Type   | Value                                                 | Value Type   |
    |:------|:-----------|:------------------------------------------------------|:-------------|
    | P_a   | `str`      | The highest dy/dx value for the user's bonding curve. | `Decimal`    |
    | P_b   | `str`      | The lowest dy/dx value for the user's bonding curve.  | `Decimal`    |
    | y     | `str`      | The token balance of the user's bonding curve.        | `int`        |
    | y_int | `str`      | The token capacity of the user's bonding curve.       | `int`        |
                
    ## Returns:
    | Return name                   | Type                               | Description                                                                                                                                                                                                 |
    |:------------------------------|:-----------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `B_precise`                   | `Decimal`                          | The precise value of `B`.                                                                                                                                                                                   |
    | `B_reconstituted`             | `int`                              | The reconstituted value of `B` from storage.                                                                                                                                                                |
    | `B_reconstitution_error`      | `float`                            | The error associated with reconstituting `B` from the mantissa and exponent, compared with its value before compression.                                                                                    |
    | `B_error_compared_to_precise` | `Decimal`                          | The error between the precise value of `B`, and its reconstituted value.                                                                                                                                    |
    | `S_precise`                   | `Decimal`                          | The precise value of `S`.                                                                                                                                                                                   |
    | `S_reconstituted`             | `int`                              | The reconstituted value of `S` from storage.                                                                                                                                                                |
    | `S_reconstitution_error`      | `float`                            | The error associated with reconstituting `S` from the mantissa and exponent, compared with its value before compression.                                                                                    |
    | `S_error_compared_to_precise` | `Decimal`                          | The error between the precise value of `S`, and its reconstituted value.                                                                                                                                    |
    | `error_profile`               | `List[Union[Decimal, int, float]]` | A list of `B_precise`, `B_reconstituted`, `B_reconstitution_error`, `B_error_compared_to_precise`, `S_precise`, `S_reconstituted`, `S_reconstitution_error`, `S_error_compared_to_precise` (in that order). |      
    
    ## Notes:
    If `return_error_profile` is set to `True`, this function will return a list with the following values:
    - `B_precise`: The precise value of `B`.
    - `B_reconstituted`: The reconstituted value of `B` from storage.
    - `B_reconstitution_error`: The error associated with reconstituting `B` from the mantissa and exponent, compared with its value before compression.
    - `B_error_compared_to_precise`: The error between the precise value of `B`, and its reconstituted value.
    - `S_precise`: The precise value of `S`.
    - `S_reconstituted`: The reconstituted value of `S` from storage.
    - `S_reconstitution_error`: The error associated with reconstituting `S` from the mantissa and exponent, compared with its value before compression.
    - `S_error_compared_to_precise`: The error between the precise value of `S`, and its reconstituted value.
    - If `return_error_profile` is set to `False`, this function returns `None`.
    
    ## Uses the following functions:
    | Function                     | Type       | Description                                                                |
    |:-----------------------------|:-----------|:---------------------------------------------------------------------------|
    | `get_user_inputs`            | `function` | Get user inputs.                                                           |
    | `process_user_inputs`        | `function` | Process user inputs and return precise and decimal values for `B` and `S`. |
    | `process_user_inputs_binary` | `function` | Convert user inputs to binary.                                             |
    | `reconstitute_number`        | `function` | Reconstitute `B` or `S` from its mantissa and exponent.                    |
    | `write_to_storage`           | `function` | Write the processed user inputs to storage.                                |
    | `measure_error`              | `function` | Measure the error between a precise number and a reconstituted number.     |
    """
    global SCALING_FACTOR
    P_a, P_b, y, y_int = get_user_inputs(user_inputs)
    B_precise, S_precise = process_user_inputs(P_a, P_b, 'precise')
    B_processed_decimal, S_processed_decimal = process_user_inputs(P_a, P_b, 'decimal')
    (S_number_of_bits,
     S_mantissa_decimal,
     S_exponent_decimal,
     B_number_of_bits,
     B_mantissa_decimal,
     B_exponent_decimal,
     S_number_binary,
     S_mantissa_binary,
     S_exponent_binary,
     B_number_binary,
     B_mantissa_binary,
     B_exponent_binary,
     y_number_of_bits,
     y_processed_binary,
     y_int_number_of_bits,
     y_int_processed_binary) = process_user_inputs_binary(S_processed_decimal, 
                                                          B_processed_decimal, 
                                                          y, 
                                                          y_int)
    (B_reconstituted, 
     B_reconstitution_error) = reconstitute_number(B_mantissa_decimal, 
                                                   B_exponent_decimal,
                                                   B_processed_decimal, 
                                                   'decimal',
                                                   get_error = True)
    (S_reconstituted, 
     S_reconstitution_error) = reconstitute_number(S_mantissa_decimal, 
                                                   S_exponent_decimal,
                                                   S_processed_decimal, 
                                                   'decimal',
                                                   get_error = True)
    write_to_storage(B_precise, S_precise, y, y_int, storage_type = 'precise')
    write_to_storage(B_processed_decimal, 
                     S_processed_decimal, 
                     y, 
                     y_int, 
                     B_number_of_bits,
                     B_mantissa_decimal,
                     B_exponent_decimal,
                     B_reconstituted,
                     B_reconstitution_error,
                     S_number_of_bits,
                     S_mantissa_decimal,
                     S_exponent_decimal,
                     S_reconstituted,
                     S_reconstitution_error,
                     y_number_of_bits,
                     y_int_number_of_bits,
                     storage_type = 'decimal')
    write_to_storage(B_number_binary, 
                     S_number_binary, 
                     y_processed_binary, 
                     y_int_processed_binary, 
                     B_number_of_bits,
                     B_mantissa_binary,
                     B_exponent_binary,
                     bin(B_reconstituted)[2:],
                     B_reconstitution_error,
                     S_number_of_bits,
                     S_mantissa_binary,
                     S_exponent_binary,
                     bin(S_reconstituted)[2:],
                     S_reconstitution_error,
                     y_number_of_bits,
                     y_int_number_of_bits,
                     storage_type = 'binary')

    B_error_compared_to_precise = measure_error(B_precise, 
                                                Decimal(B_reconstituted)/Decimal('2')**Decimal(SCALING_FACTOR))
    S_error_compared_to_precise = measure_error(S_precise, 
                                                Decimal(S_reconstituted)/Decimal('2')**Decimal(SCALING_FACTOR))
    error_profile = [B_precise, B_reconstituted, B_reconstitution_error, B_error_compared_to_precise,       
                     S_precise, S_reconstituted, S_reconstitution_error, S_error_compared_to_precise]
    return(error_profile if return_error_profile else None)


# %%
def read_from_storage(
    storage_type: str = 'decimal',
    ) -> Tuple[
               Union[str, int, Decimal], 
               Union[str, int, Decimal], 
               Union[str, int], 
               Union[str, int]]:
    """
    ### Reads the values of B, S, y, and y_int from the storage.

    ## Parameters:
    | Parameter      | Type   | Description                                                                                                                         |
    |:---------------|:-------|:------------------------------------------------------------------------------------------------------------------------------------|
    | `storage_type` | `str`  | Specifies the format in which the values are stored in the storage. Can be 'binary', 'decimal' or 'precise'. Defaults to 'decimal'. |

    ## Returns:
    | Return name   | Type                                                                                          | Description                                                                   |
    |:--------------|:----------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------|
    | `B_value`     | `Union[str, int, Decimal]`                                                                    | The processed value of `B`.                                                   |
    | `S_value`     | `Union[str, int, Decimal]`                                                                    | The processed value of `S`.                                                   |
    | `y_value`     | `Union[str, int]`                                                                             | The processed value of `y`.                                                   |
    | `y_int_value` | `Union[str, int]`                                                                             | The processed value of `y_int`.                                               |
    |               | `Tuple[Union[str, int, Decimal], Union[str, int, Decimal], Union[str, int], Union[str, int]]` | A tuple of `B_value`, `S_value`, `y_value`, and `y_int_value`, in that order. |
    
    ## Uses the following functions:
    | Function              | Type       | Description                                             |
    |:----------------------|:-----------|:--------------------------------------------------------|
    | `reconstitute_number` | `function` | Reconstitute `B` or `S` from its mantissa and exponent. |
    """
    global STORAGE
    B_value = STORAGE[storage_type]['B']['value'][-1]
    S_value = STORAGE[storage_type]['S']['value'][-1]
    y_value = STORAGE[storage_type]['y']['value'][-1]
    y_int_value = STORAGE[storage_type]['y_int']['value'][-1]
    if storage_type != 'precise':
        B_mantissa = STORAGE[storage_type]['B']['mantissa'][-1]
        B_exponent = STORAGE[storage_type]['B']['exponent'][-1]
        B_value = reconstitute_number(B_mantissa, 
                                      B_exponent, 
                                      B_value, 
                                      storage_type,
                                      get_error = False)
        S_mantissa = STORAGE[storage_type]['S']['mantissa'][-1]
        S_exponent = STORAGE[storage_type]['S']['exponent'][-1]
        S_value = reconstitute_number(S_mantissa, 
                                      S_exponent, 
                                      S_value, 
                                      storage_type,
                                      get_error = False)
    return(B_value, 
           S_value, 
           y_value, 
           y_int_value)


# %%
class SolidityUnderFlowError(Exception):
    pass

class SolidityOverFlowError(Exception):
    pass


# %%
def solidity_check_value(
    value: int
    ) -> int:
    """
    ### Checks whether an integer value is within the acceptable range, defined by global MIN_VALUE and MAX_VALUE.

    ## Parameters:
    | Parameter name   | Type   | Description                      |
    |:-----------------|:-------|:---------------------------------|
    | `value`          | `int`  | The integer value to be checked. |

    ## Returns:
    | Return name   | Type   | Description                                                      |
    |:--------------|:-------|:-----------------------------------------------------------------|
    | `value`       | `int`  | The checked integer value, if it is within the acceptable range. |

    ## Raises:
    | Error Type               | Error Description                                                                     |
    |:-------------------------|:--------------------------------------------------------------------------------------|
    | `SolidityUnderFlowError` | If the integer value is less than the minimum value defined by global `MIN_VALUE`.    |
    | `SolidityOverFlowError`  | If the integer value is greater than the maximum value defined by global `MAX_VALUE`. |
    """
    global MIN_VALUE
    global MAX_VALUE
    if value < MIN_VALUE:
        raise SolidityUnderFlowError(f'SolidityUnderFlowError: {value}')
    elif value > MAX_VALUE:
        raise SolidityOverFlowError(f'SolidityOverFlowError: {value}')
    return(value)


# %%
def solidity_addition(
    a: int, 
    b: int
    ) -> int:
    """
    ### Performs an addition operation on two integer values and checks whether the result is within the acceptable range, defined by global `MIN_VALUE` and `MAX_VALUE`.

    ## Parameters:
    | Parameter   | Type   | Description                           |
    |:------------|:-------|:--------------------------------------|
    | `a`         | `int`  | The first integer value to be added.  |
    | `b`         | `int`  | The second integer value to be added. |

    ## Returns:
    | Return   | Type   | Description                                                              |
    |:---------|:-------|:-------------------------------------------------------------------------|
    | `sum`    | `int`  | The sum of the two integer values, if it is within the acceptable range. |
    
    ## Raises:
    | Error Type               | Description                                                                   |
    |:-------------------------|:------------------------------------------------------------------------------|
    | `SolidityUnderFlowError` | If the `sum` is less than the minimum value defined by global `MIN_VALUE`.    |
    | `SolidityOverFlowError`  | If the `sum` is greater than the maximum value defined by global `MAX_VALUE`. |
    
    ## Uses the following functions:
    | Function               | Type       | Description                                                                        |
    |:-----------------------|:-----------|:-----------------------------------------------------------------------------------|
    | `solidity_check_value` | `function` | Checks whether the result of an addition operation is within the acceptable range. |
    """
    sum = solidity_check_value(a + b)
    return sum


# %%
def solidity_subtraction(
    a: int, 
    b: int
    ) -> int:
    """
    ### Performs a subtraction operation on two integer values and checks whether the result is within the acceptable range, defined by global `MIN_VALUE` and `MAX_VALUE`.

    ## Parameters:
    | Parameter   | Type   | Description                              |
    |:------------|:-------|:-----------------------------------------|
    | `a`         | `int`  | The integer value to be subtracted from. |
    | `b`         | `int`  | The integer value to be subtracted.      |

    ## Returns:
    | Return name   | Type   | Description                                                                     |
    |:--------------|:-------|:--------------------------------------------------------------------------------|
    | `difference`  | `int`  | The difference of the two integer values, if it is within the acceptable range. |

    ## Raises:
    | Raises                   | Description                                                                        |
    |:-------------------------|:-----------------------------------------------------------------------------------|
    | `SolidityUnderFlowError` | If the difference is less than the minimum value defined by global `MIN_VALUE`.    |
    | `SolidityOverFlowError`  | If the difference is greater than the maximum value defined by global `MAX_VALUE`. |
    
    ## Uses the following functions:
    | Function               | Type       | Description                                                                          |
    |:-----------------------|:-----------|:-------------------------------------------------------------------------------------|
    | `solidity_check_value` | `function` | Checks whether the result of a subtraction operation is within the acceptable range. |
    """
    difference = solidity_check_value(a - b)
    return(difference)


# %%
def solidity_multiplication(
    a: int, 
    b: int
    ) -> int:
    """
    ### Performs a multiplication operation on two integer values and checks whether the result is within the acceptable range, defined by global MIN_VALUE and MAX_VALUE.

    ## Parameters:
    | Parameter   | Type   | Description                                |
    |:------------|:-------|:-------------------------------------------|
    | `a`         | `int`  | The first integer value to be multiplied.  |
    | `b`         | `int`  | The second integer value to be multiplied. |

    ## Returns:
    | Return name   | Type   | Description                                                                  |
    |:--------------|:-------|:-----------------------------------------------------------------------------|
    | `product`     | `int`  | The product of the two integer values, if it is within the acceptable range. |

    ## Raises:
    | Raises                   | Description                                                                     |
    |:-------------------------|:--------------------------------------------------------------------------------|
    | `SolidityUnderFlowError` | If the product is less than the minimum value defined by global `MIN_VALUE`.    |
    | `SolidityOverFlowError`  | If the product is greater than the maximum value defined by global `MAX_VALUE`. |
        
    ## Uses the following functions:
    | Function               | Type       | Description                                                                             |
    |:-----------------------|:-----------|:----------------------------------------------------------------------------------------|
    | `solidity_check_value` | `function` | Checks whether the result of a multiplication operation is within the acceptable range. |
    """
    product = solidity_check_value(a * b)
    return(product)


# %%
def solidity_multiply_then_divide_floor(
    a: int, 
    b: int, 
    c: int
    ) -> int:
    """
    ### Multiplies two integers `a` and `b`, then divides the result by another integer `c` using floor division.

    ## Parameters:
    | Parameter   | Type   | Description                                |
    |:------------|:-------|:-------------------------------------------|
    | `a`         | `int`  | The first integer to be multiplied.        |
    | `b`         | `int`  | The second integer to be multiplied.       |
    | `c`         | `int`  | The integer to divide the result of `a*b`. |

    ## Returns:
    | Return name   | Type   | Description                                   |
    |:--------------|:-------|:----------------------------------------------|
    | `mulDivF`     | `int`  | The result of the floor division of `a*b//c`. |
    
    ## Uses the following functions:
    | Function               | Type       | Description                                                                                                  |
    |:-----------------------|:-----------|:-------------------------------------------------------------------------------------------------------------|
    | `solidity_check_value` | `function` | Checks whether the input value is within the acceptable range defined by global `MIN_VALUE` and `MAX_VALUE`. |
    """
    multiply_divide_floor = solidity_check_value(a*b//c)
    return(multiply_divide_floor)


# %%
def solidity_multiply_then_divide_ceiling(
    a: int, 
    b: int, 
    c: int
    ) -> int:
    """
    ### Multiplies two integers `a` and `b`, then divides the result by another integer `c` using ceiling division.

    ## Parameters:
    | Parameter   | Type   | Description                                |
    |:------------|:-------|:-------------------------------------------|
    | `a`         | `int`  | The first integer to be multiplied.        |
    | `b`         | `int`  | The second integer to be multiplied.       |
    | `c`         | `int`  | The integer to divide the result of `a*b`. |

    ## Returns:
    | Return name   | Type   | Description                                               |
    |:--------------|:-------|:----------------------------------------------------------|
    | `mulDivC`     | `int`  | The result of the ceiling division of `(a*b + c - 1)//c`. |
        
    ## Uses the following functions:
    | Function               | Type       | Description                                                                                                  |
    |:-----------------------|:-----------|:-------------------------------------------------------------------------------------------------------------|
    | `solidity_check_value` | `function` | Checks whether the input value is within the acceptable range defined by global `MIN_VALUE` and `MAX_VALUE`. |
    
    """
    multiply_divide_ceiling = solidity_check_value((a*b + c - 1)//c)
    return(multiply_divide_ceiling)


# %%
def calculate_binary_bit_truncation(
    a: str,
    b: str,
    significant_bits = 256
    ) -> str:
    """
    ### First multiplies two binary numbers, then measures the bits that overflow.

    ## Parameters:
    | Parameter          | Type   | Description                                                                       |
    |:-------------------|:-------|:----------------------------------------------------------------------------------|
    | `a`                | `str`  | The first binary number as a string.                                              |
    | `b`                | `str`  | The second binary number as a string.                                             |
    | `significant_bits` | `int`  | The number of significant bits, after which the overflow occurs. Defaults to 256. |

    ## Returns:
    | Return name      | Type   | Description                                                                                                |
    |:-----------------|:-------|:-----------------------------------------------------------------------------------------------------------|
    | `bit_truncation` | `int`  | The number of bits by which the product of the two binary numbers should be truncated to prevent overflow. |
    """
    product = bin(int(a, 2)*int(b, 2))[2:]
    bit_truncation = len(product) - significant_bits
    return(bit_truncation)


# %%
def declare_negDy_calculate_posDx(
    negDy: int, 
    storage_type: str = 'decimal'
    ) -> int:
    """
    ### Calculates the number of tokens the trader should provide to the protocol, to receive the tokens they have requested from the protocol. This function uses the fixed-point values of `B` and `S`, as calculated from the user's inputs, `P_a` and `P_b`. 

    ## Parameters:
    | Parameter      | Type   | Description                                                                                                               |
    |:---------------|:-------|:--------------------------------------------------------------------------------------------------------------------------|
    | `negDy`        | `int`  | The amount of 'y' tokens the trader is taking from the protocol (i.e. token balance transferred from protocol to trader). |
    | `storage_type` | `str`  | The storage type to be used. Can be one of 'decimal' or 'precise'. Defaults to 'decimal'.                                 |

    ## Returns:
    | Return name   | Type   | Description                                                                                                               |
    |:--------------|:-------|:--------------------------------------------------------------------------------------------------------------------------|
    | `posDx`       | `int`  | The number of 'x' tokens the protocol is taking from the trader (i.e. token balance transferred from trader to protocol). |
    
    ## Uses the following functions:
    | Function                  | Type       | Description                                                                                                                                                            |
    |:--------------------------|:-----------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `solidity_multiplication` | `function` | Performs a multiplication operation on two integer values and checks whether the result is within the acceptable range, defined by global `MIN_VALUE` and `MAX_VALUE`. |
    | `solidity_addition`       | `function` | Performs an addition operation on two integer values and checks whether the result is within the acceptable range, defined by global `MIN_VALUE` and `MAX_VALUE`.      |
    | `solidity_subtraction`    | `function` | Performs a subtraction operation on two integer values and checks whether the result is within the acceptable range, defined by global `MIN_VALUE` and `MAX_VALUE`.    |
    | `solidity_check_value`    | `function` | Checks whether the input value is within the acceptable range defined by global `MIN_VALUE` and `MAX_VALUE`.                                                           |
    | `read_from_storage`       | `function` | Reads the values of `B`, `S`, `y`, and `y_int` from the storage.                                                                                                       |
    
    ## Notes:
    - If the storage type is 'decimal', all operations are performed using fixed-point arithmetic. 
    - If the storage type is 'precise', all operations are performed using floating-point arithmetic with arbitrarily high precision. 
    """
    global SCALING_FACTOR
    global MAX_VALUE
    (B, S, y, y_int) = read_from_storage(storage_type)
    if storage_type == 'decimal':
        temp1 = solidity_multiplication(y_int, 2**SCALING_FACTOR)
        temp2 = solidity_addition(solidity_multiplication(B, y_int), solidity_multiplication(S, y))
        temp3 = solidity_subtraction(temp2, solidity_multiplication(negDy, S))
        bit_truncation = max(
            solidity_multiply_then_divide_ceiling(temp2, temp3, MAX_VALUE), 
            solidity_multiply_then_divide_ceiling(temp1, temp1, MAX_VALUE), 
            1)
        temp4 = solidity_multiply_then_divide_ceiling(temp1, temp1, bit_truncation)
        temp5 = solidity_multiply_then_divide_floor(temp2, temp3, bit_truncation)
        posDx = solidity_multiply_then_divide_ceiling(negDy, temp4, temp5)
    elif storage_type == 'precise':
        posDx = int(Decimal(negDy)*y_int**Decimal('2')/((B*y_int + S*y)*(B*y_int - S*Decimal(negDy) + S*y)))
    return(posDx)


# %%
def declare_posDx_calculate_negDy(
    posDx: int,
    storage_type: str = 'decimal'
    ) -> int:
    """
    ### Calculates the number of tokens the protocol should provide to the trader, to receive the tokens the trader wishes to sell to the protocol. This function uses the fixed-point values of `B` and `S`, as calculated from the user's inputs, `P_a` and `P_b`. 

    ## Parameters:
    | Parameter      | Type   | Description                                                                                                               |
    |:---------------|:-------|:--------------------------------------------------------------------------------------------------------------------------|
    | `posDx`        | `int`  | The number of 'x' tokens the protocol is taking from the trader (i.e. token balance transferred from trader to protocol). |
    | `storage_type` | `str`  | The storage type to be used. Can be one of 'decimal' or 'precise'. Defaults to 'decimal'.                                 |

    ## Returns:
    | Return name   | Type   | Description                                                                                                               |
    |:--------------|:-------|:--------------------------------------------------------------------------------------------------------------------------|
    | `negDy`       | `int`  | The amount of 'y' tokens the trader is taking from the protocol (i.e. token balance transferred from protocol to trader). |
    
    ## Uses the following functions:
    | Function                                | Type       | Description                                                                                                                                                            |
    |:----------------------------------------|:-----------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `read_from_storage`                     | `function` | Reads the values of `B`, `S`, `y`, and `y_int` from the storage.                                                                                                       |
    | `solidity_multiplication`               | `function` | Performs a multiplication operation on two integer values and checks whether the result is within the acceptable range, defined by global `MIN_VALUE` and `MAX_VALUE`. |
    | `solidity_addition`                     | `function` | Performs an addition operation on two integer values and checks whether the result is within the acceptable range, defined by global `MIN_VALUE` and `MAX_VALUE`.      |
    | `solidity_multiply_then_divide_ceiling` | `function` | Multiplies two integers `a` and `b`, then divides the result by another integer `c` using ceiling division.                                                            |
    | `solidity_multiply_then_divide_floor`   | `function` | Multiplies two integers `a` and `b`, then divides the result by another integer `c` using floor division.                                                              |
    
    ## Notes:
    - If the storage type is 'decimal', all operations are performed using fixed-point arithmetic. 
    - If the storage type is 'precise', all operations are performed using floating-point arithmetic with arbitrarily high precision. 
    """
    global SCALING_FACTOR
    global MAX_VALUE
    (B, S, y, y_int) = read_from_storage(storage_type)
    if storage_type == 'decimal':
        temp1 = solidity_multiplication(y_int, 2**SCALING_FACTOR)
        temp2 = solidity_addition(solidity_multiplication(y, S), solidity_multiplication(y_int, B))
        temp3 = solidity_multiplication(temp2, posDx)
        truncator = max(
            solidity_multiply_then_divide_ceiling(temp3, S, MAX_VALUE), 
            solidity_multiply_then_divide_ceiling(temp1, temp1, MAX_VALUE),
            1)
        temp4 = solidity_multiply_then_divide_ceiling(temp1, temp1, truncator)
        temp5 = solidity_multiply_then_divide_ceiling(temp3, S, truncator)
        negDy = solidity_multiply_then_divide_floor(temp2, temp3//truncator, solidity_addition(temp4, temp5))
    elif storage_type == 'precise':
        negDy = int(posDx*(B*y_int + S*y)**Decimal('2')/(posDx*S*(B*y_int + S*y) + y_int**Decimal('2')))
    return(negDy)


# %%
trade_functions ={
    'declare_negDy_calculate_posDx' : declare_negDy_calculate_posDx,
    'declare_posDx_calculate_negDy' : declare_posDx_calculate_negDy
}


# %%
def read_input_parameters(
    input_parameters: Dict[str, int]
    ) -> Tuple[Union[int, Decimal]]:
    """
    ### Retrieves values from the input dictionary and returns them as a tuple.

    ## Parameters:
    | Parameter          | Type   | Description                                            |
    |:-------------------|:-------|:-------------------------------------------------------|
    | `input_parameters` | `dict` | A dictionary containing the following key-value pairs: |
        
    ## Parameters Dictionary:
    | Key                    | Key Type   | Value                                                                                            | Value Type   |
    |:-----------------------|:-----------|:-------------------------------------------------------------------------------------------------|:-------------|
    | pb_start               | `str`      | The precise starting value of `P_b`.                                                             | `Decimal`    |
    | pb_stop                | `str`      | The precise ending value of `P_b`.                                                               | `Decimal`    |
    | pb_number_of_points    | `str`      | The number of points between `P_b_start` and `P_b_stop` to be included in the primary array.     | `int`        |
    | s_start                | `str`      | The precise starting value of `S`.                                                               | `Decimal`    |
    | s_stop                 | `str`      | The precise ending value of `S`.                                                                 | `Decimal`    |
    | s_number_of_points     | `str`      | The number of points between `S_start` and `S_stop` to be included in the primary array.         | `int`        |
    | y_int_start            | `str`      | The starting value of `y_int`.                                                                   | `int`        |
    | y_int_stop             | `str`      | The ending value of `y_int`.                                                                     | `int`        |
    | y_int_number_of_points | `str`      | The number of points between `y_int_start` and `y_int_stop` to be included in the primary array. | `int`        |
    | secondary_array_n      | `str`      | The value by which the secondary array values will be divided.                                   | `int`        |

    ## Returns:
    | Return name   | Type                  | Description                                                                                                                                                                                         |
    |:--------------|:----------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    |               | `Union[int, Decimal]` | A tuple of `pb_start`, `pb_stop`, `pb_number_of_points`, `s_start`, `s_stop`, `s_number_of_points`, `y_int_start`, `y_int_stop`, `y_int_number_of_points`, and `secondary_array_n` (in that order). |
    """
    min_value = input_parameters['min_value']
    max_value = input_parameters['max_value']
    max_B_and_S_bits = input_parameters['max_B_and_S_bits']
    mantissa_bits = input_parameters['mantissa_bits']
    exponent_bits = input_parameters['exponent_bits']
    scaling_factor = input_parameters['scaling_factor']
    P_b_start = input_parameters['P_b_start']
    P_b_stop = input_parameters['P_b_stop']
    P_b_number_of_points = input_parameters['P_b_number_of_points']
    S_start = input_parameters['S_start']
    S_stop = input_parameters['S_stop']
    S_number_of_points = input_parameters['S_number_of_points']
    y_int_start = input_parameters['y_int_start']
    y_int_stop = input_parameters['y_int_stop']
    y_int_number_of_points = input_parameters['y_int_number_of_points']
    secondary_array_n = input_parameters['secondary_array_n']
    return(min_value, max_value, max_B_and_S_bits,
           mantissa_bits,
           exponent_bits,
           scaling_factor,
           P_b_start,
           P_b_stop,
           P_b_number_of_points,
           S_start,
           S_stop,
           S_number_of_points,
           y_int_start,
           y_int_stop,
           y_int_number_of_points,
           secondary_array_n)


# %%
def generate_primary_array(
    start: int, 
    stop: int, 
    number_of_points: int,
    include_zero: bool = False,
    integers_only: bool = False
    ) -> List[Union[int, Decimal]]:
    """
    ### Generates an array of integers or Decimal objects that represent the values of `2**i`, where `i` is a range of exponents obtained by dividing the range `start` to `stop` into `number_of_points` equal parts.

    ## Parameters:
    | Parameter          | Type   | Description                                                                                                                          |
    |:-------------------|:-------|:-------------------------------------------------------------------------------------------------------------------------------------|
    | `start`            | `int`  | The lower limit of the range of exponents used to calculate `2**i`.                                                                  |
    | `stop`             | `int`  | The upper limit of the range of exponents used to calculate `2**i`.                                                                  |
    | `number_of_points` | `int`  | The number of points in the generated array.                                                                                         |
    | `include_zero`     | `bool` | If `True`, 0 will be included as the first element of the generated array. Defaults to `False`.                                      |
    | `integers_only`    | `bool` | If `True`, only integers will be included in the generated array. If `False`, Decimal objects will be included. Defaults to `False`. |

    ## Returns:
    | Return name   | Type                        | Description                                                                      |
    |:--------------|:----------------------------|:---------------------------------------------------------------------------------|
    |               | `List[Union[int, Decimal]]` | A list of integers or Decimal objects representing the calculated `2**i` values. |

    ## Example:
    To generate an array of 5 Decimal objects that represent the values of `2**i`, where `i` is a range of exponents from 0 to 4, you can call the function with the following parameters:
    >>> generate_primary_array(start = 0, 
                               stop = 4, 
                               number_of_points = 5, 
                               integers_only = False)
    [Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16')]
    """
    array = [Decimal('2')**Decimal(int(i)) for i in np.linspace(start, stop, num = number_of_points, endpoint = True)]
    if include_zero:
        array.insert(0, Decimal('0'))
    if integers_only:
        array = [int(i) for i in array]
    return(array)


# %%
def generate_secondary_array(
    number: int, 
    n: int = 2) -> List[int]:
    """
    ### Generates a secondary array of integers, logarithmically spaced between 1 and `number`; this method guarnatees that both 1 and `number` are included in the returned array.

    ## Parameters:
    | Parameter   | Type   | Description                                                              |
    |:------------|:-------|:-------------------------------------------------------------------------|
    | `number`    | `int`  | The maximum value in the secondary array.                                |
    | `n`         | `int`  | The number of times to take the geometric means. The default value is 2. |

    ## Returns:
    | Return name       | Type        | Description                                                                 |
    |:------------------|:------------|:----------------------------------------------------------------------------|
    | `secondary_array` | `List[int]` | A list of integers representing the logarithmically spaced secondary array. |
        
    ## Example:
    >>> generate_secondary_array(100, 3)
    [1, 1, 3, 5, 10, 17, 31, 56, 100]
    
    ## Notes:
    - The secondary array is generated by taking `n` consecutive geometric means of `number`. 
    - Each pair of consecutive values in the resulting list has a ratio of approximately `number**(1/n)`. 
    - The length of the resulting list is `2**n + 1`.
    - Both 1 and `number` are guaranteed to be included in the returned array.
    - Due to the integer mapping, some elements in the list may appear more than once. 
    """
    secondary_array = [Decimal('1'), Decimal(number)]
    for i in range(n):
        new_values = []
        for j in range(len(secondary_array) - 1):
            new_value = Decimal.sqrt(secondary_array[j] * secondary_array[j+1])
            new_values.extend([secondary_array[j], new_value])
        new_values.append(secondary_array[-1])
        secondary_array = new_values
    secondary_array = list(map(int, secondary_array))
    return(secondary_array)


# %%
def calculate_P_a_from_P_b_and_S(
    P_b: Decimal, 
    S: Decimal
    ) -> Decimal:
    """
    ### Calculates the value of `P_a` using `P_b` and `S` values.

    ## Parameters:
    | Parameter   | Type      | Description                 |
    |:------------|:----------|:----------------------------|
    | `P_b`       | `Decimal` | The precise value of `P_b`. |
    | `S`         | `Decimal` | The precise value of `S`.   |

    ## Returns:
    | Return name   | Type      | Description                 |
    |:--------------|:----------|:----------------------------|
    | `P_a`         | `Decimal` | The precise value of `P_a`. |
        
    ## Example:
    >>> P_b = Decimal('1.123456')
    >>> S = Decimal('1234567891234123.456789')
    >>> calculate_P_a_for_array(P_b, S)
    Decimal('29.65889756954754979380483802844400125319067809889103623018190973399900631933122415858776572527721419')
    """
    global SCALING_FACTOR
    P_a = (S/Decimal('2')**SCALING_FACTOR + Decimal.sqrt(P_b))**Decimal('2')
    return(P_a)


# %%
def calculate_max_posDx(    
    P_b: Decimal,
    S: Decimal,
    y: int,
    y_int: int):
    """
    ### Calculates the maximum positive value of `Dx` from `P_b`, `S`, `y`, and `y_int` values.

    ## Parameters:
    | Parameter   | Type      | Description                                                                         |
    |:------------|:----------|:------------------------------------------------------------------------------------|
    | `P_b`       | `Decimal` | The precise value of the curve parameter `P_b` (refer to the carbon whitepaper).    |
    | `S`         | `Decimal` | The precise value of the curve parameter `S` (refer to the carbon whitepaper).      |
    | `y`         | `int`     | The integer value of the curve token balance, `y` (refer to the carbon whitepaper). |
    | `y_int`     | `int`     | The integer value of the curve parameter `y_int` (refer to the carbon whitepaper).  |

    ## Returns:
    | Return name   | Type   | Description                                                                                                            |
    |:--------------|:-------|:-----------------------------------------------------------------------------------------------------------------------|
    | `max_posDx`   | `int`  | The maximum swap amount `Dx` required for the return token amount `Dy` to be equal to the remaining token balance `y`. |

    ## Raises:
    | Raises             | Description                                                                                                                                   |
    |:-------------------|:----------------------------------------------------------------------------------------------------------------------------------------------|
    | `InvalidOperation` | If the calculation results in an invalid operation, such as the square root of a negative number (should never occur under normal operation). |
    | `DivisionByZero`   | If the calculation results in a division by zero (can occur for `B` = 0).                                                                     |

    ## Examples:
    >>> P_b = Decimal('0')
    >>> S = Decimal('123.123456')
    >>> y = 2000000000
    >>> y_int = 4000000000
    >>> calculate_max_posDx(P_b, S, y, y_int)
    5192296858534827628530496329220095
    >>> P_b = Decimal('0.00000000012345679')
    >>> S = Decimal('0')
    >>> y = 123456789
    >>> y_int = 987654321
    >>> calculate_max_posDx(P_b, S, y, y_int)
    999999991899999991
    
    ## Notes:
    - In the case of an `InvalidOperation`, `max_posDx` is forced to zero. This condition is unknown to the normal parameter space.
    - In the case of a `DivisionByZero`, `max_posDx` is forced to the largest possible trade quantity, `2**112 - 1`.
    """
    if y == 0:
        max_posDx = 0
    else: 
        try:
            max_posDx = int(Decimal(y)*Decimal(y_int)/(Decimal.sqrt(P_b)*(Decimal.sqrt(P_b)*Decimal(y_int) + S*Decimal(y))))
        except InvalidOperation:
            max_posDx = 0
        except DivisionByZero:
            max_posDx = 2**112 - 1
    return(max_posDx)


# %%
def generate_array_matrix(
    P_b_array : List[Decimal], 
    S_array : List[Decimal], 
    y_int_array : List[int],
    secondary_array_n : int
    ) -> List[List[int]]:
    """
    ### Generates a matrix of primary and secondary input values for use in exploring error profiles.
    
    ## Parameters:
    | Parameter   | Type      | Description                                                                         |
    |:------------|:----------|:------------------------------------------------------------------------------------|
    | `P_b`       | `Decimal` | The precise value of the curve parameter `P_b` (refer to the carbon whitepaper).    |
    | `S`         | `Decimal` | The precise value of the curve parameter `S` (refer to the carbon whitepaper).      |
    | `y`         | `int`     | The integer value of the curve token balance, `y` (refer to the carbon whitepaper). |
    | `y_int`     | `int`     | The integer value of the curve parameter `y_int` (refer to the carbon whitepaper).  |
    
    ## Returns
    | Return name   | Type   | Description                                                                                                            |
    |:--------------|:-------|:-----------------------------------------------------------------------------------------------------------------------|
    | `max_posDx`   | `int`  | The maximum swap amount `Dx` required for the return token amount `Dy` to be equal to the remaining token balance `y`. |

    ## Raises:
    | Raises           | Description                                                               |
    |:-----------------|:--------------------------------------------------------------------------|
    | `DivisionByZero` | If the calculation results in a division by zero (can occur for `B` = 0). |
    
    ## Example:
    >>> P_b_array = generate_primary_array(-10, 10, 10)
    >>> S_array = generate_primary_array(-20, 20, 10)
    >>> y_int_array = generate_primary_array(0, 10, 11, integers_only=True)
    >>> generate_array_matrix(P_b_array, S_array, y_int_array, 2)
    [[Decimal('0.0009765625...'), Decimal('0.0009765625'), 1, 1, 1, 1],
     [Decimal('0.0009765625...'), Decimal('0.0009765625'), 1, 1, 5, 1],
     [Decimal('0.0009765625...'), Decimal('0.0009765625'), 1, 1, 31, 1],
     [Decimal('0.0009765625...'), Decimal('0.0009765625'), 1, 1, 180, 1],
     [...]
     [Decimal('1024.0000002384...'), Decimal('1024'), 1024, 1024, 0, 5],
     [Decimal('1024.0000002384...'), Decimal('1024'), 1024, 1024, 0, 32],
     [Decimal('1024.0000002384...'), Decimal('1024'), 1024, 1024, 0, 181],
     [Decimal('1024.0000002384...'), Decimal('1024'), 1024, 1024, 0, 1024]]
     
    ## Notes:
     - The matrix includes integer values for `P_a`, `P_b`, `y`, `y_int`, `posDx`, and `negDy` for every combination of `P_b`, `S`, and `y_int`.
    
    ## Uses the following functions:
    | Function                       | Return Type   | Description                                                                                                               |
    |:-------------------------------|:--------------|:--------------------------------------------------------------------------------------------------------------------------|
    | `calculate_P_a_from_P_b_and_S` | `function`    | Calculates the precise value of `P_a` from precise `P_b` and precise `S` values.                                          |
    | `generate_secondary_array`     | `function`    | Generates a secondary array of integers, logarithmically spaced between 1 and `y` or `max_posDx` depending on context.    |
    | `calculate_max_posDx`          | `function`    | Calculates the maximum swap amount `posDx` from the available liquidity `y`, and curve parameters `P_b`, `S`, and `y_int` |
    """
    array_matrix = []
    for P_b in P_b_array:
        for S in S_array:
            P_a = calculate_P_a_from_P_b_and_S(P_b, S)
            for y_int in y_int_array:
                y_array = generate_secondary_array(y_int, secondary_array_n)
                for y in y_array:
                    try:
                        max_posDx = calculate_max_posDx(P_b, S, y, y_int)
                    except DivisionByZero:
                        max_posDx = (2**112 - 1)
                    posDx_array = generate_secondary_array(max_posDx, secondary_array_n)
                    negDy_array = generate_secondary_array(y, secondary_array_n)
                    for i in range(2**secondary_array_n + 1):
                        array_matrix.append([P_a, P_b, y, y_int, posDx_array[i], negDy_array[i]]) 
    return(array_matrix)


# %%
def generate_input_matrices(
    input_parameters: Dict[str, int], 
    ) -> List[List[Union[Decimal, int]]]:
    """
    ### Generates an array matrix of primary and secondary input values used to explore error profiles.

    ## Parameters:
    | Parameter          | Type                             | Description                                                                                                      |
    |:-------------------|:---------------------------------|:-----------------------------------------------------------------------------------------------------------------|
    | `input_parameters` | `Dict[str, Union[int, Decimal]]` | A dictionary containing the input parameters for the error profile analysis, with the following key-value pairs: |
        
    ## Parameters Dictionary:
    | Key                      | Key Type   | Value                                                                                                                                                         | Value Type   |
    |:-------------------------|:-----------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------|
    | `min_value`              | `str`      | The minimum allowable value for any input, output, or intermediate computation.                                                                               | `int`        |
    | `max_value`              | `str`      | The maximum allowable value for any input, output, or intermediate computation.                                                                               | `int`        |
    | `max_B_and_S_bits`       | `str`      | The maximum number of bits to be used to store the `B` and `S` values.                                                                                        | `int`        |
    | `mantissa_bits`          | `str`      | The maximum number of bits to be used to store the mantissa of `B` and S.                                                                                     | `int`        |
    | `exponent_bits`          | `str`      | The maximum number of bits to be used to store the exponent of `B` and S.                                                                                     | `int`        |
    | `scaling_factor`         | `str`      | The log2 of the global scaling factor (i.e. output = `2**input`).                                                                                             | `int`        |
    | `P_b_start`              | `str`      | The log2 of the starting point for the `P_b` primary array (i.e. output = `2**input`).                                                                        | `int`        |
    | `P_b_stop`               | `str`      | The log2 of the stopping point for the `P_b` primary array (i.e. output = `2**input`).                                                                        | `int`        |
    | `P_b_number_of_points`   | `str`      | The number of the points to be generated between `P_b_start` and `P_b_stop`.                                                                                  | `int`        |
    | `S_start`                | `str`      | The log2 of the starting point for the `S` primary array (i.e. output = `2**input`).                                                                          | `int`        |
    | `S_stop`                 | `str`      | The log2 of the stopping point for the `S` primary array (i.e. output = `2**input`).                                                                          | `int`        |
    | `S_number_of_points`     | `str`      | The number of points to be generated between `S_start` and `S_stop`.                                                                                          | `int`        |
    | `y_int_start`            | `str`      | The log2 of the starting point for the `y_int` primary array (i.e. output = `2**input`).                                                                      | `int`        |
    | `y_int_stop`             | `str`      | The log2 of the stopping point for the `y_int` primary array (i.e. output = `2**input`).                                                                      | `int`        |
    | `y_int_number_of_points` | `str`      | The number of points to be generated between `y_int_start` and `y_int_stop`.                                                                                  | `int`        |
    | `secondary_array_n`      | `str`      | The number of times to divide the range between 1 and its maximum. The resulting list contains `2**input + 1` integers, evenly spaced on a logarithmic scale. | `int`        |

    ## Returns:
    | Return name    | Type                              | Description                                                                    |
    |:---------------|:----------------------------------|:-------------------------------------------------------------------------------|
    | `array_matrix` | `List[List[Union[int, Decimal]]]` | A matrix of primary and secondary input values used to explore error profiles. |
    
    ## Example:
    >>> input_parameters = {'min_value' : int(0), 
                            'max_value' : int(2**256 - 1),
                            'max_B_and_S_bits' : int(96), 
                            'mantissa_bits' : int(48), 
                            'exponent_bits' : int(6),
                            'scaling_factor' : int(48), 
                            'P_b_start' : int(50), 
                            'P_b_stop' : int(-50), 
                            'P_b_number_of_points' : int(50), 
                            'S_start' : int(50), 
                            'S_stop' : int(-50), 
                            'S_number_of_points' : int(50), 
                            'y_int_start' : int(0), 
                            'y_int_stop' : int(112), 
                            'y_int_number_of_points' : int(50), 
                            'secondary_array_n' : int(3)}
    >>> generate_input_matrices(input_parameters)
    [[Decimal('0'), Decimal('0'), 1, 1, 1, 1],
    [Decimal('0'), Decimal('0'), 1, 1, 16383, 1],
    [Decimal('0'), Decimal('0'), 1, 1, 268435455, 1],
    [...]
    [Decimal('8.881784197001252323390934135687878160012750078027800038862777179195860200516401852174080167153801693E-16'),
     Decimal('8.8817841970012523233890533447265625E-16'),
     5192296858534827628530496329220096,
     5192296858534827628530496329220096,
     3759624434215916222073277607420212938,
     19342813113834066795298816],
    [Decimal('8.881784197001252323390934135687878160012750078027800038862777179195860200516401852174080167153801693E-16'),
     Decimal('8.8817841970012523233890533447265625E-16'),
     5192296858534827628530496329220096,
     5192296858534827628530496329220096,
     4688154051479578499194734583362381942135942,
     316912650057057350374175801344],
    [Decimal('8.881784197001252323390934135687878160012750078027800038862777179195860200516401852174080167153801693E-16'),
     Decimal('8.8817841970012523233890533447265625E-16'),
     5192296858534827628530496329220096,
     5192296858534827628530496329220096,
     5846006375099045001590949829944662617401361174527,
     5192296858534827628530496329220096]]
    
    ## Uses the following functions:
    | Function                 | Type          | Description                                                                                                                                                                                                  |
    |:-------------------------|:--------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `read_input_parameters`  | `function`    | Retrieves values from the input dictionary and returns them as a `tuple`.                                                                                                                                    |
    | `generate_primary_array` | `function`    | Generates an array of `int` or `Decimal` objects that represent the values of `2^i`, where `i` is a range of exponents obtained by dividing the range `start` to `stop` into `number_of_points` equal parts. |
    | `generate_array_matrix`  | `function`    | Generates a matrix of primary and secondary input values for use in exploring error profiles.                                                                                                                |
        
    """
    global MIN_VALUE
    global MAX_VALUE
    global MAX_B_AND_S_BITS
    global MANTISSA_BITS
    global EXPONENT_BITS
    global SCALING_FACTOR
    
    (min_value,
     max_value,
     max_B_and_S_bits,
     mantissa_bits,
     exponent_bits,
     scaling_factor,
     pb_start,
     pb_stop,
     pb_number_of_points,
     s_start,
     s_stop,
     s_number_of_points,
     y_int_start,
     y_int_stop,
     y_int_number_of_points,
     secondary_array_n) = read_input_parameters(input_parameters)
    
    MIN_VALUE = min_value
    MAX_VALUE = max_value
    MAX_B_AND_S_BITS = max_B_and_S_bits
    MANTISSA_BITS = mantissa_bits
    EXPONENT_BITS = exponent_bits
    SCALING_FACTOR = scaling_factor
    
    P_b_array = generate_primary_array(pb_start,
                                       pb_stop,
                                       pb_number_of_points,
                                       include_zero = True,
                                       integers_only = False)
    S_array = generate_primary_array(s_start,
                                     s_stop,
                                     s_number_of_points,
                                     include_zero = True,
                                     integers_only = False)
    y_int_array = generate_primary_array(y_int_start,
                                         y_int_stop,
                                         y_int_number_of_points,
                                         include_zero = False,
                                         integers_only = True)
    array_matrix = generate_array_matrix(P_b_array,
                                         S_array,
                                         y_int_array,
                                         secondary_array_n)
    return(array_matrix)


# %%
def run_all_inputs(
    input_matrix: List[List[Union[Decimal, int]]],
    ) -> List[List[Union[Decimal, int]]]:
    """
    ### Runs error profile analysis and trade simulations for a matrix of primary and secondary input values. 

    ## Parameters:
    | Parameter      | Type                              | Description                                                                    |
    |:---------------|:----------------------------------|:-------------------------------------------------------------------------------|
    | `input_matrix` | `List[List[Union[Decimal, int]]]` | A matrix of primary and secondary input values used to explore error profiles. |

    ## Returns:
    | Return name     | Type                                   | Description                                                |
    |:----------------|:---------------------------------------|:-----------------------------------------------------------|
    | `output_matrix` | `List[List[Union[Decimal, int, str]]]` | The `input_matrix` with additional columns appended to it. |
        
    ## Example:
    >>> input_parameters = {
        'min_value' : int(0),
        'max_value' : int(2**256 - 1),
        'max_B_and_S_bits' : int(96),
        'mantissa_bits' : int(48),
        'exponent_bits' : int(6),
        'scaling_factor' : int(48),
        'P_b_start' : int(1), 
        'P_b_stop' : int(-1), 
        'P_b_number_of_points' : int(3),
        'S_start' : int(2), 
        'S_stop' : int(-2), 
        'S_number_of_points' : int(3),
        'y_int_start' : int(10), 
        'y_int_stop' : int(20), 
        'y_int_number_of_points' : int(3), 
        'secondary_array_n' : int(2) 
        }
    >>> input_matrix = generate_input_matrices(input_parameters)
    >>> run_all_inputs(input_matrix)
    [[Decimal('0'), Decimal('0'), 1, 1024, 1, 1, Decimal('0'), 0, 0, 0, Decimal('0'), 0, 0, 0, 0, 0, 'ZeroDivisionError', 'ZeroDivisionError', 0, 0],
     [Decimal('0'), Decimal('0'), 1, 1024, 268435455, 1, Decimal('0'), 0, 0, 0, Decimal('0'), 0, 0, 0, 0, 0, 'ZeroDivisionError', 'ZeroDivisionError', 0, 0],
     [Decimal('0'), Decimal('0'), 1, 1024, 72057594037927935, 1, Decimal('0'), 0, 0, 0, Decimal('0'), 0, 0, 0, 0, 0, 'ZeroDivisionError', 'ZeroDivisionError', 0, 0],
     [...]
     [Decimal('0.500000...'), Decimal('0.5'), 1048576, 1048576, 1244, 1024, Decimal('0.707106...'), 199032864766430, 0, Decimal('-1.972762...E-15'), 
      Decimal('8.881784...E-16'), 0, 0, Decimal('-1'), 622, 621, 2047, 2049, -0.001607717041800643, 0.0009770395701025891],
     [Decimal('0.500000...'), Decimal('0.5'), 1048576, 1048576, 43915, 32768, Decimal('0.707106...'), 199032864766430, 0, Decimal('-1.972762...E-15'), 
      Decimal('8.881784...E-16'), 0, 0, Decimal('-1'), 21957, 21957, 65535, 65537, 0, 3.0518043793392844e-05],
     [Decimal('0.500000...'), Decimal('0.5'), 1048576, 1048576, 1549367, 1048576, Decimal('0.707106...'), 199032864766430, 0, Decimal('-1.972762...E-15'), 
      Decimal('8.881784...E-16'), 0, 0, Decimal('-1'), 774683, 774683, 2097151, 2097153, 0, 9.536747711538177e-07]]]
    
    ## Notes:
    - For each set of input values in `input_matrix`, the function performs the following:
    - Runs an error profile analysis on the user input values using `process_user_inputs_and_write_to_storage`.
    - Records the results of the error profile analysis in `input_matrix`.
    - Runs two trade simulations on `posDx` and `negDy` values, using both `precise` and `decimal` storage types, and records the results and errors in `output_matrix`.
    - The output matrix contains the original `input_matrix` columns, plus:
    - Error profile analysis results (`B`, `S`, max/min values, etc.)
    - Simulated output values for `posDx` and `negDy` using `precise` and `decimal` storage types.
    - Error measurements for the trade simulations.
    
    ## Uses the following functions:
    | Function                                   | Type          | Description                                                                                                                            |
    |:-------------------------------------------|:--------------|:---------------------------------------------------------------------------------------------------------------------------------------|
    | `process_user_inputs_and_write_to_storage` | `function`    | Processes the user inputs and writes the results to the global storage variables.                                                      |
    | `measure_error`                            | `function`    | Measures the error between trade outputs computed with fixed-point arithmetic, and floating-point arithmetic with arbitrary precision. |
    """
    global SCALING_FACTOR
    for i, array in enumerate(input_matrix):
        user_inputs = {
            'P_a' : array[0], 
            'P_b' : array[1],
            'y' : array[2],
            'y_int' : array[3],
            }
        B_and_S_error_profile = process_user_inputs_and_write_to_storage(user_inputs, return_error_profile = True)
        input_matrix[i].extend(B_and_S_error_profile)
        trade_outputs = []
        for j, mode in enumerate(['declare_posDx_calculate_negDy',
                                  'declare_negDy_calculate_posDx']):
            for storage_type in ['precise', 
                                 'decimal']:
                try:
                    trade_outputs.append(trade_functions[mode](array[4 + j], storage_type))
                except ZeroDivisionError:
                    trade_outputs.append('ZeroDivisionError')
                except SolidityUnderFlowError:
                    trade_outputs.append('SolidityUnderFlowError')
                except SolidityOverFlowError:
                    trade_outputs.append('SolidityOverFlowError')
                except InvalidOperation:
                    trade_outputs.append('InvalidOperation')
        trade_errors = [measure_error(trade_outputs[k], trade_outputs[1 + k]) for k in range(0, 4, 2)]
        array.extend(trade_outputs)
        array.extend(trade_errors)
    output_matrix = input_matrix
    return(output_matrix)


# %%
def calculate_error_profile(
    input_parameters: Dict[str, int], 
    filename: str = 'test_error_profiling_1'
    ) -> pd.DataFrame:
    """
    ### Calculates error profiles for a set of input parameters.
    
    ## Parameters:
    | Parameter          | Type                             | Description                                                                                                      |
    |:-------------------|:---------------------------------|:-----------------------------------------------------------------------------------------------------------------|
    | `input_parameters` | `Dict[str, Union[int, Decimal]]` | A dictionary containing the input parameters for the error profile analysis, with the following key-value pairs: |
    | `filename`         | `str`                            | A tag, appended as a prefix to the dataframes during their generation.                                           |
        
    ## Parameters Dictionary:
    | Key                      | Key Type   | Value                                                                                                                                                         | Value Type   |
    |:-------------------------|:-----------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------|
    | `min_value`              | `str`      | The minimum allowable value for any input, output, or intermediate computation.                                                                               | `int`        |
    | `max_value`              | `str`      | The maximum allowable value for any input, output, or intermediate computation.                                                                               | `int`        |
    | `max_B_and_S_bits`       | `str`      | The maximum number of bits to be used to store the `B` and `S` values.                                                                                        | `int`        |
    | `mantissa_bits`          | `str`      | The maximum number of bits to be used to store the mantissa of `B` and S.                                                                                     | `int`        |
    | `exponent_bits`          | `str`      | The maximum number of bits to be used to store the exponent of `B` and S.                                                                                     | `int`        |
    | `scaling_factor`         | `str`      | The log2 of the global scaling factor (i.e. output = `2**input`).                                                                                             | `int`        |
    | `P_b_start`              | `str`      | The log2 of the starting point for the `P_b` primary array (i.e. output = `2**input`).                                                                        | `int`        |
    | `P_b_stop`               | `str`      | The log2 of the stopping point for the `P_b` primary array (i.e. output = `2**input`).                                                                        | `int`        |
    | `P_b_number_of_points`   | `str`      | The number of the points to be generated between `P_b_start` and `P_b_stop`.                                                                                  | `int`        |
    | `S_start`                | `str`      | The log2 of the starting point for the `S` primary array (i.e. output = `2**input`).                                                                          | `int`        |
    | `S_stop`                 | `str`      | The log2 of the stopping point for the `S` primary array (i.e. output = `2**input`).                                                                          | `int`        |
    | `S_number_of_points`     | `str`      | The number of points to be generated between `S_start` and `S_stop`.                                                                                          | `int`        |
    | `y_int_start`            | `str`      | The log2 of the starting point for the `y_int` primary array (i.e. output = `2**input`).                                                                      | `int`        |
    | `y_int_stop`             | `str`      | The log2 of the stopping point for the `y_int` primary array (i.e. output = `2**input`).                                                                      | `int`        |
    | `y_int_number_of_points` | `str`      | The number of points to be generated between `y_int_start` and `y_int_stop`.                                                                                  | `int`        |
    | `secondary_array_n`      | `str`      | The number of times to divide the range between 1 and its maximum. The resulting list contains `2**input + 1` integers, evenly spaced on a logarithmic scale. | `int`        |

    ## Returns:
    | Return name       | Type           | Description                                              |
    |:------------------|:---------------|:---------------------------------------------------------|
    | `main_data_frame` | `pd.DataFrame` | A comprehensive record of the results of the simulation: |
    
    ## Return DataFrame:
    | Column name                              | Series description                                                                                                                          | Series Type   |
    |:-----------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------|:--------------|
    | precise input P_a (Decimal)              | The user input and curve parameter, `P_a`, with arbitrary floating-point precision.                                                         | `float`       |
    | precise input P_b (Decimal)              | The user input and curve parameter, `P_a`, with arbitrary floating-point precision.                                                         | `float`       |
    | y (int)                                  | The user input and token balance of the curve, `y`, as an integer.                                                                          | `int`         |
    | y intercept (int)                        | The user input and token balance of the curve,, `y_int`, as an integer.                                                                     | `int`         |
    | input posDx (int)                        | The user input and trade quantity requested to deliver to the protocol, `posDx`, as an integer.                                             | `int`         |
    | input negDy (int)                        | The user input and trade quantity requested to sequester from the protocol, `negDy`, as an integer.                                         | `int`         |
    | B precise (Decimal)                      | The `B` value, calculated with arbitrary floating-point precision from the user input `P_b`.                                                | `float`       |
    | B reconstituted (int)                    | The `B` integer value after reconstitution from storage (i.e. some precision loss due to compression/decompression)                         | `int`         |
    | error in B reconstitution (Decimal)      | The specific relative error in the `B` value attributed to compression/decompression only.                                                  | `float`       |
    | error in B compared to precise (Decimal) | The general relative error in the `B` value, calculated from its reconstituted value versus its precise value.                              | `float`       |
    | S precise (Decimal)                      | The `S` value, calculated with high precision from the user inputs `P_a` and `P_b`.                                                         | `float`       |
    | S reconstituted (int)                    | The `S` value after reconstitution from storage (i.e. some precision loss due to compression/decompression).                                | `int`         |
    | error in S reconstitution (Decimal)      | The specific relative error in the `S` value attributed to compression/decompression only.                                                  | `float`       |
    | error in S compared to precise (Decimal) | The general relative error in the `S` value, calculated from its reconstituted value versus its precise value.                              | `float`       |
    | precise output negDy (int)               | The integer result of `negDy`, calculated with arbitrary floating-point precision from the user input `posDx`.                              | `float`       |
    | output negDy (int)                       | The fixed-point output `negDy`, calculated from the user input `posDx` and while emulating the constraints of the Ethereum Virtual Machine. | `int`         |
    | precise output posDx (int)               | The integer result of `posDx`, calculated with arbitrary floating-point precision from the user input `negDy`.                              | `int`         |
    | output posDx (int)                       | The fixed-point output `posDx`, calculated from the user input `negDy` and while emulating the constraints of the Ethereum Virtual Machine. | `int`         |
    | error in output negDy (Decimal)          | The specific relative error between the fixed-point, and high-precision `negDy` outputs calculated from identical, integer `posDx` inputs.  | `float`       |
    | error in output posDx (Decimal)          | The specific relative error between the fixed-point, and high-precision `posDx` outputs calculated from identical, integer `negDy` inputs.  | `float`       |
    | id (int)                                 | The 'original' index number, which is maintained in all future slicing and other manipulations of this dataframe.                           | `int`         |

    ## Saves:
    | Output             | Type                             | Description                                                                                                                                        |
    |:-------------------|:---------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------|
    | `main_data_frame`  | `pd.DataFrame`                   | A pandas DataFrame containing the results of the error profile analysis is saved as a pickle file with the name filename+'_FULL_DATAFRAME.pickle'. |
    | `input_parameters` | `Dict[str, Union[int, Decimal]]` | A dictionary of the input parameters used in the analysis is saved as a pickle file with the name filename+'_INPUT_DICTIONARY.pickle'.             |
    
    ## Notes:
    - The function generates an input array matrix based on the provided input parameters, and then runs an analysis of error profiles for each input value. 
    - The results of the analysis are recorded in a pandas DataFrame and stored to disk in a pickle file.
    - The input parameters is also stored to disk in a pickle file.
    
    ## Uses the following functions:
    | Function                  | Return Type   | Description                                                                                           |
    |:--------------------------|:--------------|:------------------------------------------------------------------------------------------------------|
    | `generate_input_matrices` | `function`    | Generates an array matrix of primary and secondary input values used to explore error profiles.       |
    | `run_all_inputs`          | `function`    | Runs error profile analysis and trade simulations for a matrix of primary and secondary input values. |
    """
    column_names = ['precise input P_a (Decimal)', 'precise input P_b (Decimal)', 'y (int)', 'y intercept (int)', 'input posDx (int)', 'input negDy (int)',
                    'B precise (Decimal)', 'B reconstituted (int)', 'error in B reconstitution (Decimal)', 'error in B compared to precise (Decimal)', 'S precise (Decimal)',
                    'S reconstituted (int)', 'error in S reconstitution (Decimal)', 'error in S compared to precise (Decimal)', 'precise output negDy (int)', 'output negDy (int)',           
                    'precise output posDx (int)', 'output posDx (int)', 'error in output negDy (Decimal)', 'error in output posDx (Decimal)']
    input_matrices = generate_input_matrices(input_parameters)
    main_data_frame = pd.DataFrame(run_all_inputs(input_matrices), columns = column_names).astype(float, errors = 'ignore').drop_duplicates()
    main_data_frame.reset_index(drop = True, inplace = True)
    main_data_frame['id (int)'] = list(main_data_frame.index)
    main_data_frame.to_pickle(f'{filename}_FULL_DATAFRAME.pickle')
    with open(f'{filename}_INPUT_DICTIONARY.pickle', 'wb') as f:
        pickle.dump(input_parameters, f)
    return(main_data_frame)


# %%
def split_main_dataframe_by_input_type(
    main_data_frame: pd.DataFrame,
    comparison: bool = False,
    suffix_list: Union[List[str], None] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    ### Splits the input dataframe into two smaller dataframes based on the input type.
    
    ## Parameters:
    | Parameter         | Type                     | Description                                                                                                                    |
    |:------------------|:-------------------------|:-------------------------------------------------------------------------------------------------------------------------------|
    | `main_data_frame` | `pd.DataFrame`           | A comprehensive record of the results of the simulation.                                                                       |
    | `comparison`      | `bool`                   | If `True`, the function will look for non-null numeric values in two columns that have different suffixes. Default is `False`. |
    | `suffix_list`     | `Union[List[str], None]` | The suffixes to be added to the output column names. Only applicable if comparison is True. Default is `None`.                 |

    ## Parameters DataFrame:    
    | Column Name                              | Series Description                                                                                                                          | Series Type   |
    |:-----------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------|:--------------|
    | precise input P_a (Decimal)              | The user input and curve parameter, `P_a`, with arbitrary floating-point precision.                                                         | `float`       |
    | precise input P_b (Decimal)              | The user input and curve parameter, `P_a`, with arbitrary floating-point precision.                                                         | `float`       |
    | y (int)                                  | The user input and token balance of the curve, `y`, as an integer.                                                                          | `int`         |
    | y intercept (int)                        | The user input and token balance of the curve,, `y_int`, as an integer.                                                                     | `int`         |
    | input posDx (int)                        | The user input and trade quantity requested to deliver to the protocol, `posDx`, as an integer.                                             | `int`         |
    | input negDy (int)                        | The user input and trade quantity requested to sequester from the protocol, `negDy`, as an integer.                                         | `int`         |
    | B precise (Decimal)                      | The `B` value, calculated with arbitrary floating-point precision from the user input `P_b`.                                                | `float`       |
    | B reconstituted (int)                    | The `B` integer value after reconstitution from storage (i.e. some precision loss due to compression/decompression)                         | `int`         |
    | error in B reconstitution (Decimal)      | The specific relative error in the `B` value attributed to compression/decompression only.                                                  | `float`       |
    | error in B compared to precise (Decimal) | The general relative error in the `B` value, calculated from its reconstituted value versus its precise value.                              | `float`       |
    | S precise (Decimal)                      | The `S` value, calculated with high precision from the user inputs `P_a` and `P_b`.                                                         | `float`       |
    | S reconstituted (int)                    | The `S` value after reconstitution from storage (i.e. some precision loss due to compression/decompression).                                | `int`         |
    | error in S reconstitution (Decimal)      | The specific relative error in the `S` value attributed to compression/decompression only.                                                  | `float`       |
    | error in S compared to precise (Decimal) | The general relative error in the `S` value, calculated from its reconstituted value versus its precise value.                              | `float`       |
    | precise output negDy (int)               | The integer result of `negDy`, calculated with arbitrary floating-point precision from the user input `posDx`.                              | `float`       |
    | output negDy (int)                       | The fixed-point output `negDy`, calculated from the user input `posDx` and while emulating the constraints of the Ethereum Virtual Machine. | `int`         |
    | precise output posDx (int)               | The integer result of `posDx`, calculated with arbitrary floating-point precision from the user input `negDy`.                              | `int`         |
    | output posDx (int)                       | The fixed-point output `posDx`, calculated from the user input `negDy` and while emulating the constraints of the Ethereum Virtual Machine. | `int`         |
    | error in output negDy (Decimal)          | The specific relative error between the fixed-point, and high-precision `negDy` outputs calculated from identical, integer `posDx` inputs.  | `float`       |
    | error in output posDx (Decimal)          | The specific relative error between the fixed-point, and high-precision `posDx` outputs calculated from identical, integer `negDy` inputs.  | `float`       |
    | id (int)                                 | The 'original' index number, which is maintained in all future slicing and other manipulations of this dataframe.                           | `int`         |
             
    ## Returns:
    | Return name                          | Type                  | Description                                                                                              |
    |:-------------------------------------|:----------------------|:---------------------------------------------------------------------------------------------------------|
    | `input_posDx_output_negDy_DataFrame` | `pd.DataFrame`        | A sliced subset of the input dataframe.                                                                  |
    | `input_negDy_output_posDx_DataFrame` | `pd.DataFrame`        | A sliced subset of the input dataframe.                                                                  |
    |                                      | `Tuple[pd.DataFrame]` | A tuple of `input_posDx_output_negDy_DataFrame` and `input_negDy_output_posDx_DataFrame`, in that order. |
        
    ## Returned DataFrames:  
    | Column Name                     | Series Description                                                                                                                          | Series Type   |
    |:--------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------|:--------------|
    | y (int)                         | The user input, `y`, as an integer.                                                                                                         | `int`         |
    | y intercept (int)               | The user input, `y_int`, as an integer.                                                                                                     | `int`         |
    | B precise (Decimal)             | The `B` value, calculated with arbitrary floating-point precision from the user input `P_b`.                                                | `float`       |
    | S precise (Decimal)             | The `S` value, calculated with high precision from the user inputs `P_a` and `P_b`.                                                         | `float`       |
    | input posDx (int)               | The user input, `posDx`, as an integer.                                                                                                     | `int`         |
    | precise output negDy (int)      | The integer result of `negDy`, calculated with arbitrary floating-point precision from the user input `posDx`.                              | `int`         |
    | output negDy (int)              | The fixed-point output `negDy`, calculated from the user input `posDx` and while emulating the constraints of the Ethereum Virtual Machine. | `int`         |
    | error in output negDy (Decimal) | The specific relative error between the fixed-point, and high-precision `negDy` outputs calculated from identical, integer `posDx` inputs.  | `float`       |
    | id (int)                        | The 'original' index number, which is maintained in all future slicing and other manipulations of this dataframe.                           | `int`         |
            
        
    | Column Name                     | Series Description                                                                                                                          | Series Type   |
    |:--------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------|:--------------|
    | y (int)                         | The user input and token balance of the curve, `y`, as an integer.                                                                          | `int`         |
    | y intercept (int)               | The user input and token balance of the curve,, `y_int`, as an integer.                                                                     | `int`         |
    | B precise (Decimal)             | The `B` value, calculated with arbitrary floating-point precision from the user input `P_b`.                                                | `float`       |
    | S precise (Decimal)             | The `S` value, calculated with high precision from the user inputs `P_a` and `P_b`.                                                         | `float`       |
    | input negDy (int)               | The user input and trade quantity requested to sequester from the protocol, `negDy`, as an integer.                                         | `int`         |
    | precise output posDx (int)      | The integer result of `posDx`, calculated with arbitrary floating-point precision from the user input `negDy`.                              | `int`         |
    | output posDx (int)              | The fixed-point output `posDx`, calculated from the user input `negDy` and while emulating the constraints of the Ethereum Virtual Machine. | `int`         |
    | error in output posDx (Decimal) | The specific relative error between the fixed-point, and high-precision `posDx` outputs calculated from identical, integer `negDy` inputs.  | `float`       |
    | id (int)                        | The 'original' index number, which is maintained in all future slicing and other manipulations of this dataframe.                           | `int`         |
        
    ## Notes:
    - One of the smaller dataframes, `input_posDx_output_negDy_DataFrame`, contains rows with 'input posDx' as input.
    - The other smaller dataframe, `input_negDy_output_posDx_DataFrame`, contains rows with 'input negDy' as input.
    - If comparison = True, a second column corresponding to the error in the output from the comparison data set is included for each daughter dataframe:
    - The columns from the original dataframe that are not included in either of the returned dataframes are dropped entirely:
    
    ## Dropped columns:
    | Column name                              | Series description                                                                                           | Series Type   |
    |:-----------------------------------------|:-------------------------------------------------------------------------------------------------------------|:--------------|
    | precise input P_a (Decimal)              | The user input, P_a, with high precision.                                                                    | `float`       |
    | precise input P_b (Decimal)              | The user input, P_b, with high precision.                                                                    | `float`       |
    | B reconstituted (int)                    | The B value after reconstitution from storage (i.e. some precision loss due to compression/decompression).   | `int`         |
    | error in B reconstitution (Decimal)      | The specific relative error in the B value attributed to compression/decompression only.                     | `float`       |
    | error in B compared to precise (Decimal) | The general relative error in the B value, calculated from its reconstituted value versus its precise value. | `float`       |
    | S reconstituted (int)                    | The S value after reconstitution from storage (i.e. some precision loss due to compression/decompression).   | `int`         |
    | error in S reconstitution (Decimal)      | The specific relative error in the S value attributed to compression/decompression only.                     | `float`       |
    | error in S compared to precise (Decimal) | The general relative error in the S value, calculated from its reconstituted value versus its precise value. | `float`       |
    """
    column_names = {
    'shared_cols' : [ 'y (int)', 'y intercept (int)', 'B precise (Decimal)', 'S precise (Decimal)', 'id (int)'],
    'input_posDx_output_negDy_cols' : ['input posDx (int)', 'precise output negDy (int)', 'output negDy (int)', 'error in output negDy (Decimal)'],
    'input_negDy_output_posDx_cols' : ['input negDy (int)', 'precise output posDx (int)', 'output posDx (int)', 'error in output posDx (Decimal)']
    }
    if comparison:
        column_names['input_posDx_output_negDy_cols'] = ['input posDx (int)', 'precise output negDy (int)', 
                                                         f'output negDy (int){suffix_list[0]}', f'error in output negDy (Decimal){suffix_list[0]}', 
                                                         f'output negDy (int){suffix_list[1]}', f'error in output negDy (Decimal){suffix_list[1]}']
        column_names['input_negDy_output_posDx_cols'] = ['input negDy (int)', 'precise output posDx (int)', 
                                                         f'output posDx (int){suffix_list[0]}', f'error in output posDx (Decimal){suffix_list[0]}',
                                                         f'output posDx (int){suffix_list[1]}', f'error in output posDx (Decimal){suffix_list[1]}']
    input_posDx_output_negDy_cols = column_names['shared_cols'] + column_names['input_posDx_output_negDy_cols'] 
    input_negDy_output_posDx_cols = column_names['shared_cols'] + column_names['input_negDy_output_posDx_cols'] 
    input_posDx_output_negDy_DataFrame = main_data_frame.loc[:, input_posDx_output_negDy_cols].reset_index(drop = True)
    input_negDy_output_posDx_DataFrame = main_data_frame.loc[:, input_negDy_output_posDx_cols].reset_index(drop = True)
    return(input_posDx_output_negDy_DataFrame, input_negDy_output_posDx_DataFrame)


# %%
def get_paused_strategies_mask(
    dataframe_to_mask: pd.DataFrame
    ) -> pd.Series:
    """
    ### Returns a boolean mask indicating which rows have both B precise and S precise equal to 0.

    ## Parameters:
    | Parameter           | Type           | Description                         |
    |:--------------------|:---------------|:------------------------------------|
    | `dataframe_to_mask` | `pd.DataFrame` | The DataFrame to apply the mask to. |

    ## Returns:
    | Return name            | Type        | Description                                                                            |
    |:-----------------------|:------------|:---------------------------------------------------------------------------------------|
    | `paused_strategy_mask` | `pd.Series` | A boolean mask indicating which rows have both `B` precise and `S` precise equal to 0. |
    """
    paused_strategy_mask = (dataframe_to_mask['B precise (Decimal)'] == 0) & (dataframe_to_mask['S precise (Decimal)'] == 0)
    return(paused_strategy_mask)


# %%
def get_numeric_errors_only_mask(
    dataframe_to_mask: pd.DataFrame, 
    output_type: str,
    ) -> pd.Series:
    """
    ### Returns a boolean mask indicating which rows have non-null, numeric values for the specified output error column.

    ## Parameters:
    | Parameter Name      | Type           | Description                                                      |
    |:--------------------|:---------------|:-----------------------------------------------------------------|
    | `dataframe_to_mask` | `pd.DataFrame` | The DataFrame to apply the mask to.                              |
    | `output_type`       | `str`          | The output type to apply the mask to, either 'negDy' or 'posDx'. |

    ## Returns:
    | Return name                | Type        | Description                                                                                               |
    |:---------------------------|:------------|:----------------------------------------------------------------------------------------------------------|
    | `numeric_errors_only_mask` | `pd.Series` | A boolean mask indicating which rows have non-null, numeric values for the specified output error column. |

    """
    numeric_errors_only_mask = pd.notnull(pd.to_numeric(dataframe_to_mask[f'error in output {output_type} (Decimal)'].replace('infinity', np.nan), errors='coerce'))
    return(numeric_errors_only_mask)


# %%
def get_infinity_errors_only_mask(
    dataframe_to_mask: pd.DataFrame, 
    output_type: str
    ) -> pd.Series:
    """
    ### Returns a boolean mask indicating which rows have 'infinity' values in the specified output error column.

    ## Parameters:
    | Parameter           | Type           | Description                                                     |
    |:--------------------|:---------------|:----------------------------------------------------------------|
    | `dataframe_to_mask` | `pd.DataFrame` | The DataFrame to apply the mask to.                             |
    | `output_type`       | `str`          | The output type to apply the mask to, either `negDy` or `posDx` |

    ## Returns:
    | Return name            | Type        | Description                                                                                       |
    |:-----------------------|:------------|:--------------------------------------------------------------------------------------------------|
    | `infinity_errors_mask` | `pd.Series` | A boolean mask indicating which rows have 'infinity' values in the specified output error column. |
    """
    infinity_errors_mask = dataframe_to_mask[f'error in output {output_type} (Decimal)'] == 'infinity'
    return(infinity_errors_mask)


# %%
def get_precise_numeric_outputs_only_mask(
    dataframe_to_mask: pd.DataFrame, 
    output_type: str
    ) -> pd.Series:
    """
    ### Returns a boolean mask indicating which rows have non-null, numeric values for the specified precise output column.

    ## Parameters:
    | Parameter Name      | Type           | Description                                                      |
    |:--------------------|:---------------|:-----------------------------------------------------------------|
    | `dataframe_to_mask` | `pd.DataFrame` | The DataFrame to apply the mask to.                              |
    | `output_type`       | `str`          | The output type to apply the mask to, either 'negDy' or 'posDx'. |

    ## Returns:
    | Return name                         | Type        | Description                                                                                                 |
    |:------------------------------------|:------------|:------------------------------------------------------------------------------------------------------------|
    | `precise_numeric_outputs_only_mask` | `pd.Series` | A boolean mask indicating which rows have non-null, numeric values for the specified precise output column. |
    """
    precise_numeric_outputs_only_mask = pd.notnull(pd.to_numeric(dataframe_to_mask[f'precise output {output_type} (int)'], errors='coerce'))
    return(precise_numeric_outputs_only_mask)


# %%
def mask_dataframe_and_return_negated_dataframe(
    dataframe_to_mask: pd.DataFrame, 
    mask: pd.Series
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    ### Returns two DataFrames, one with the rows that match the given mask and one with the rows that don't match the mask.

    ## Parameters:
    | Parameter Name      | Type           | Description                                 |
    |:--------------------|:---------------|:--------------------------------------------|
    | `dataframe_to_mask` | `pd.DataFrame` | The DataFrame to apply the mask to.         |
    | `mask`              | `pd.Series`    | The boolean mask to apply to the DataFrame. |

    ## Returns:
    | Return name   | Type                              | Description                                                                                                  |
    |:--------------|:----------------------------------|:-------------------------------------------------------------------------------------------------------------|
    |               | Tuple[pd.DataFrame, pd.DataFrame] | Two DataFrames, one with the rows that match the given mask and one with the rows that don't match the mask. |
    """
    masked_dataframe = dataframe_to_mask[mask].reset_index(drop = True)
    negated_masked_dataframe = dataframe_to_mask[~mask].reset_index(drop = True)
    return(masked_dataframe, negated_masked_dataframe)


# %%
class UndefinedBehaviorException(Exception):
    """
    ### Exception raised when an undefined behavior is detected in the simulation.

    ## Attributes:
    | Attribute Name   | Type           | Description                                                                                       |
    |:-----------------|:---------------|:--------------------------------------------------------------------------------------------------|
    | `dataframe`      | `pd.DataFrame` | The output dataframe containing an example situation not thought to exist at the time of writing. |
    """
    def __init__(self, dataframe):
        """
        ### Initializes the `UndefinedBehaviorException` instance.

        ## Parameters:
        | Parameter Name   | Type           | Description                                 |
        |:-----------------|:---------------|:--------------------------------------------|
        | `dataframe`      | `pd.DataFrame` | The input dataframe with undefined behavior |
        """
        self.dataframe = dataframe
        expected_errors_dictionary = {
        'precise value' : ['number', 
                        'ZeroDivisionError', 
                        '0 (int)', 
                        'number', 
                        '???'],
        'fixed point value' : ['number', 
                            'ZeroDivisionError', 
                            'number', 
                            'SolidityOverFlowError OR SolidityUnderFlowError', 
                            '???'],
        'error' : ['number', 
                '0 (int)', 
                'infinity', 
                'N/A', 
                'N/A'],
        'notes' : ['Normal; both fixed point and arbitrary precision calculations produced numbers. No problems.',
                'Expected if (B == 0 AND S == 0), OR (B == 0 AND input negDy == y).',
                'Expected if the fixed point output posDx <= 2 and precise output posDx < 1 (i.e. = 0).',
                'Normal; any intermediate computation may not exceed 256 bits (except for mulDiv).',
                'The currentrly unprecedented situation in which you have found yourself.']
        }
        message = f"""
UNDEFINED BEHAVIOR DETECTED; REVIEW IMMEDIATELY! URGENT! \n
\n
A situation was detected that is outside the scope of the simulation, and should be carefully reviewed. \n
\n
The following table summarises the expected behavior (of both the product, and this simulation): \n
Expected Behavior: \n
\n
{tabulate(expected_errors_dictionary, headers='keys', tablefmt='simple')} \n
\n
The inputs in this dataframe are alleged to have given rise to a situation that is not depicted above: \n
\n
Dataframe: \n
\n
{tabulate(self.dataframe, headers='keys', tablefmt='simple')} \n
\n
DO NOT IGNORE. \n
\n
A binary file with the suffix '_UNDEFINED_BEHAVIOR_DataFrame.pickle' has been saved to your local machine. \n
\n
Please send this file and this error message to mark@bancor.network for a $5 reward. \n
        """
        super().__init__(message)


# %%
def check_empty_dataframes(
    input_posDx_output_negDy_UNDEFINED_BEHAVIOR_DataFrame: pd.DataFrame, 
    input_negDy_output_posDx_UNDEFINED_BEHAVIOR_DataFrame: pd.DataFrame
    ) -> None:
    """
    ### Check if any of the input dataframes contains an undefined behavior, and raise an exception if so.

    ## Parameters:
    | Parameter Name                                          | Type               | Description                                                                                                                                       |
    |:--------------------------------------------------------|:-------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------|
    | `input_posDx_output_negDy_UNDEFINED_BEHAVIOR_DataFrame` | `pandas.DataFrame` | The remains of an input `posDx` output `negDy` dataframe, from which all sets of expected behaviors have been extracted. Thus it should be empty. |
    | `input_negDy_output_posDx_UNDEFINED_BEHAVIOR_DataFrame` | `pandas.DataFrame` | The remains of an input `negDy` output `posDx` dataframe, from which all sets of expected behaviors have been extracted. Thus it should be empty. |

    ## Raises:
    | Raises                       | Description                                                                                      |
    |:-----------------------------|:-------------------------------------------------------------------------------------------------|
    | `UndefinedBehaviorException` | If either dataframe contains a condition that was not extracted with the rest of the processing. |
    """
    if len(input_posDx_output_negDy_UNDEFINED_BEHAVIOR_DataFrame) > 0:
        raise UndefinedBehaviorException(input_posDx_output_negDy_UNDEFINED_BEHAVIOR_DataFrame)
    if len(input_negDy_output_posDx_UNDEFINED_BEHAVIOR_DataFrame) > 0:
        raise UndefinedBehaviorException(input_negDy_output_posDx_UNDEFINED_BEHAVIOR_DataFrame)
    return(None)


# %%
def process_main_data_frame(
    main_data_frame: pd.DataFrame, 
    filename: str = 'test_error_profiling'
    ) -> None:
    """
    ### Processes the input dataframe by filtering and cleaning its contents.
    
    ## Parameters:
    | Parameter Name    | Type           | Description                                                            |
    |:------------------|:---------------|:-----------------------------------------------------------------------|
    | `main_data_frame` | `pd.DataFrame` | A comprehensive record of the results of the simulation.               |
    | `filename`        | `str`          | A tag, appended as a prefix to the dataframes during their generation. |
        
    ## Parameters DataFrame:    
    | Column Name                              | Series Description                                                                                                                          | Series Type   |
    |:-----------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------|:--------------|
    | precise input P_a (Decimal)              | The user input and curve parameter, `P_a`, with arbitrary floating-point precision.                                                         | `float`       |
    | precise input P_b (Decimal)              | The user input and curve parameter, `P_a`, with arbitrary floating-point precision.                                                         | `float`       |
    | y (int)                                  | The user input and token balance of the curve, `y`, as an integer.                                                                          | `int`         |
    | y intercept (int)                        | The user input and token balance of the curve,, `y_int`, as an integer.                                                                     | `int`         |
    | input posDx (int)                        | The user input and trade quantity requested to deliver to the protocol, `posDx`, as an integer.                                             | `int`         |
    | input negDy (int)                        | The user input and trade quantity requested to sequester from the protocol, `negDy`, as an integer.                                         | `int`         |
    | B precise (Decimal)                      | The `B` value, calculated with arbitrary floating-point precision from the user input `P_b`.                                                | `float`       |
    | B reconstituted (int)                    | The `B` integer value after reconstitution from storage (i.e. some precision loss due to compression/decompression)                         | `int`         |
    | error in B reconstitution (Decimal)      | The specific relative error in the `B` value attributed to compression/decompression only.                                                  | `float`       |
    | error in B compared to precise (Decimal) | The general relative error in the `B` value, calculated from its reconstituted value versus its precise value.                              | `float`       |
    | S precise (Decimal)                      | The `S` value, calculated with high precision from the user inputs `P_a` and `P_b`.                                                         | `float`       |
    | S reconstituted (int)                    | The `S` value after reconstitution from storage (i.e. some precision loss due to compression/decompression).                                | `int`         |
    | error in S reconstitution (Decimal)      | The specific relative error in the `S` value attributed to compression/decompression only.                                                  | `float`       |
    | error in S compared to precise (Decimal) | The general relative error in the `S` value, calculated from its reconstituted value versus its precise value.                              | `float`       |
    | precise output negDy (int)               | The integer result of `negDy`, calculated with arbitrary floating-point precision from the user input `posDx`.                              | `float`       |
    | output negDy (int)                       | The fixed-point output `negDy`, calculated from the user input `posDx` and while emulating the constraints of the Ethereum Virtual Machine. | `int`         |
    | precise output posDx (int)               | The integer result of `posDx`, calculated with arbitrary floating-point precision from the user input `negDy`.                              | `int`         |
    | output posDx (int)                       | The fixed-point output `posDx`, calculated from the user input `negDy` and while emulating the constraints of the Ethereum Virtual Machine. | `int`         |
    | error in output negDy (Decimal)          | The specific relative error between the fixed-point, and high-precision `negDy` outputs calculated from identical, integer `posDx` inputs.  | `float`       |
    | error in output posDx (Decimal)          | The specific relative error between the fixed-point, and high-precision `posDx` outputs calculated from identical, integer `negDy` inputs.  | `float`       |
    | id (int)                                 | The 'original' index number, which is maintained in all future slicing and other manipulations of this dataframe.                           | `int`         |

    ## Saves:
    | Saved item                                              | Type           | Description                                                                                                                                                                                                                         |
    |:--------------------------------------------------------|:---------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `input_posDx_output_negDy_PAUSED_DataFrame`             | `pd.DataFrame` | pandas DataFrame containing only the paused strategies (i.e. where both `B` and `S` values are exactly zero) for all `posDX` inputs and `negDy` outputs (as a pickle file).                                                         |
    | `input_posDx_output_negDy_NUMERIC_ERRORS_DataFrame`     | `pd.DataFrame` | pandas DataFrame containing only the remaining data after the above filter was applied, and where the error in the 'error in output negDy (Decimal)' is numeric for all posDx inputs and negDy outputs as (a pickle file).          |
    | `input_posDx_output_negDy_INFINITY_ERRORS_DataFrame`    | `pd.DataFrame` | pandas DataFrame containing only the remaining data after the two above filters were applied, and where the error in the 'error in output negDy (Decimal)' is 'infintiy' for all posDx inputs and negDy outputs (as a pickle file). |
    | `input_posDx_output_negDy_SOLIDITY_ERRORS_DataFrame`    | `pd.DataFrame` | pandas DataFrame containing only the remaining data after the three above filter were applied, and where the 'precise output negDy (int)' is numeric for all posDx inputs and negDy outputs (as a pickle file).                     |
    | `input_posDx_output_negDy_UNDEFINED_BEHAVIOR_DataFrame` | `pd.DataFrame` | pandas DataFrame containing only the remaining data after the four above filters were applied for all posDx inputs and negDy outputs (as a pickle file). Input patterns within this set are potentially exploitable.                |
    | `input_negDy_output_posDx_PAUSED_DataFrame`             | `pd.DataFrame` | pandas DataFrame containing only the paused strategies (i.e. where both B and S values are exactly zero) for all posDX inputs and negDy outputs (as a pickle file).                                                                 |
    | `input_negDy_output_posDx_NUMERIC_ERRORS_DataFrame`     | `pd.DataFrame` | pandas DataFrame containing only the remaining data after the above filter was applied, and where the error in the 'error in output posDx (Decimal)' is numeric for all negDy inputs and posDx (outputs as a pickle file).          |
    | `input_negDy_output_posDx_INFINITY_ERRORS_DataFrame`    | `pd.DataFrame` | pandas DataFrame containing only the remaining data after the two above filters were applied, and where the error in the 'error in output posDx (Decimal)' is 'infintiy' for all negDy inputs and posDx outputs (as a pickle file). |
    | `input_negDy_output_posDx_SOLIDITY_ERRORS_DataFrame`    | `pd.DataFrame` | pandas DataFrame containing only the remaining data after the three above filters was applied, and where the 'precise output posDx (int)' is numeric for all negDy inputs and posDx outputs (as a pickle file).                     |
    | `input_negDy_output_posDx_UNDEFINED_BEHAVIOR_DataFrame` | `pd.DataFrame` | pandas DataFrame containing only the remaining data after the four above filters were applied for all negDy inputs and posDx outputs (as a pickle file). Input patterns within this set should be interrogated carefully.           |

    ## Returns:
    None

    ## Notes:
    - The columns from the original dataframe that are dropped entirely (i.e. not included in any of the sliced dataframes) are:

    ## Dropped columns:
    | Column name                              | Series description                                                                                           | Series Type   |
    |:-----------------------------------------|:-------------------------------------------------------------------------------------------------------------|:--------------|
    | precise input P_a (Decimal)              | The user input, P_a, with high precision.                                                                    | `float`       |
    | precise input P_b (Decimal)              | The user input, P_b, with high precision.                                                                    | `float`       |
    | B reconstituted (int)                    | The B value after reconstitution from storage (i.e. some precision loss due to compression/decompression).   | `int`         |
    | error in B reconstitution (Decimal)      | The specific relative error in the B value attributed to compression/decompression only.                     | `float`       |
    | error in B compared to precise (Decimal) | The general relative error in the B value, calculated from its reconstituted value versus its precise value. | `float`       |
    | S reconstituted (int)                    | The S value after reconstitution from storage (i.e. some precision loss due to compression/decompression).   | `int`         |
    | error in S reconstitution (Decimal)      | The specific relative error in the S value attributed to compression/decompression only.                     | `float`       |
    | error in S compared to precise (Decimal) | The general relative error in the S value, calculated from its reconstituted value versus its precise value. | `float`       |

    ## Uses the following functions:
    | Function                                      | Type       | Description                                                                                                          |
    |:----------------------------------------------|:-----------|:---------------------------------------------------------------------------------------------------------------------|
    | `split_main_dataframe_by_input_type`          | `function` | Splits the main DataFrame into two separate DataFrames based on the input type.                                      |
    | `get_paused_strategies_mask`                  | `function` | Returns a boolean mask indicating which rows have both `B precise` and `S precise` equal to 0.                       |
    | `mask_dataframe_and_return_negated_dataframe` | `function` | Returns two DataFrames, one with the rows that match the given mask and one with the rows that don't match the mask. |
    | `get_numeric_errors_only_mask`                | `function` | Returns a boolean mask indicating which rows have non-null, numeric values for the specified output error column.    |
    | `get_infinity_errors_only_mask`               | `function` | Returns a boolean mask indicating which rows have 'infinity' values in the specified output error column.            |
    | `get_precise_numeric_outputs_only_mask`       | `function` | Returns a boolean mask indicating which rows have non-null, numeric values for the specified precise output column.  |
    | `check_empty_dataframes`                      | `function` | Checks if any of the input dataframes contains an undefined behavior, and raises an exception if so.                 |
    """
    (input_posDx_output_negDy_DataFrame, input_negDy_output_posDx_DataFrame) = split_main_dataframe_by_input_type(main_data_frame)
    input_posDx_output_negDy_paused_strategy_mask = get_paused_strategies_mask(input_posDx_output_negDy_DataFrame)
    input_negDy_output_posDx_paused_strategy_mask = get_paused_strategies_mask(input_negDy_output_posDx_DataFrame)
    (input_posDx_output_negDy_PAUSED_DataFrame, 
     input_posDx_output_negDy_DataFrame) = mask_dataframe_and_return_negated_dataframe(input_posDx_output_negDy_DataFrame, 
                                                                                       input_posDx_output_negDy_paused_strategy_mask)
    (input_negDy_output_posDx_PAUSED_DataFrame, 
     input_negDy_output_posDx_DataFrame) = mask_dataframe_and_return_negated_dataframe(input_negDy_output_posDx_DataFrame, 
                                                                                       input_negDy_output_posDx_paused_strategy_mask)
    input_posDx_output_negDy_numeric_errors_only_mask = get_numeric_errors_only_mask(input_posDx_output_negDy_DataFrame, 'negDy')
    input_negDy_output_posDx_numeric_errors_only_mask = get_numeric_errors_only_mask(input_negDy_output_posDx_DataFrame, 'posDx')
    (input_posDx_output_negDy_NUMERIC_ERRORS_DataFrame, 
     input_posDx_output_negDy_DataFrame) = mask_dataframe_and_return_negated_dataframe(input_posDx_output_negDy_DataFrame, 
                                                                                       input_posDx_output_negDy_numeric_errors_only_mask)
    (input_negDy_output_posDx_NUMERIC_ERRORS_DataFrame, 
     input_negDy_output_posDx_DataFrame) = mask_dataframe_and_return_negated_dataframe(input_negDy_output_posDx_DataFrame, 
                                                                                       input_negDy_output_posDx_numeric_errors_only_mask)
    input_posDx_output_negDy_infinity_errors_only_mask = get_infinity_errors_only_mask(input_posDx_output_negDy_DataFrame, 'negDy')
    input_negDy_output_posDx_infinity_errors_only_mask = get_infinity_errors_only_mask(input_negDy_output_posDx_DataFrame, 'posDx')
    (input_posDx_output_negDy_INFINITY_ERRORS_DataFrame, 
     input_posDx_output_negDy_DataFrame) = mask_dataframe_and_return_negated_dataframe(input_posDx_output_negDy_DataFrame, 
                                                                                       input_posDx_output_negDy_infinity_errors_only_mask)
    (input_negDy_output_posDx_INFINITY_ERRORS_DataFrame, 
     input_negDy_output_posDx_DataFrame) = mask_dataframe_and_return_negated_dataframe(input_negDy_output_posDx_DataFrame, 
                                                                                       input_negDy_output_posDx_infinity_errors_only_mask)
    input_posDx_output_negDy_precise_numeric_outputs_only_mask = get_precise_numeric_outputs_only_mask(input_posDx_output_negDy_DataFrame, 'negDy')
    input_negDy_output_posDx_precise_numeric_outputs_only_mask = get_precise_numeric_outputs_only_mask(input_negDy_output_posDx_DataFrame, 'posDx')
    (input_posDx_output_negDy_SOLIDITY_ERRORS_DataFrame, 
     input_posDx_output_negDy_UNDEFINED_BEHAVIOR_DataFrame) = mask_dataframe_and_return_negated_dataframe(input_posDx_output_negDy_DataFrame, 
                                                                                                          input_posDx_output_negDy_precise_numeric_outputs_only_mask)
    (input_negDy_output_posDx_SOLIDITY_ERRORS_DataFrame, 
     input_negDy_output_posDx_UNDEFINED_BEHAVIOR_DataFrame) = mask_dataframe_and_return_negated_dataframe(input_negDy_output_posDx_DataFrame, 
                                                                                                          input_negDy_output_posDx_precise_numeric_outputs_only_mask)
    processed_dataframes = [input_posDx_output_negDy_PAUSED_DataFrame, input_negDy_output_posDx_PAUSED_DataFrame,
                            input_posDx_output_negDy_NUMERIC_ERRORS_DataFrame, input_negDy_output_posDx_NUMERIC_ERRORS_DataFrame,
                            input_posDx_output_negDy_INFINITY_ERRORS_DataFrame, input_negDy_output_posDx_INFINITY_ERRORS_DataFrame,
                            input_posDx_output_negDy_SOLIDITY_ERRORS_DataFrame, input_negDy_output_posDx_SOLIDITY_ERRORS_DataFrame,
                            input_posDx_output_negDy_UNDEFINED_BEHAVIOR_DataFrame, input_negDy_output_posDx_UNDEFINED_BEHAVIOR_DataFrame]
    filenames = [f'{filename}_input_posDx_output_negDy_PAUSED_DataFrame.pickle', f'{filename}_input_negDy_output_posDx_PAUSED_DataFrame.pickle',
                 f'{filename}_input_posDx_output_negDy_NUMERIC_ERRORS_DataFrame.pickle', f'{filename}_input_negDy_output_posDx_NUMERIC_ERRORS_DataFrame.pickle',
                 f'{filename}_input_posDx_output_negDy_INFINITY_ERRORS_DataFrame.pickle', f'{filename}_input_negDy_output_posDx_INFINITY_ERRORS_DataFrame.pickle',
                 f'{filename}_input_posDx_output_negDy_SOLIDITY_ERRORS_DataFrame.pickle', f'{filename}_input_negDy_output_posDx_SOLIDITY_ERRORS_DataFrame.pickle',
                 f'{filename}_input_posDx_output_negDy_UNDEFINED_BEHAVIOR_DataFrame.pickle', f'{filename}_input_negDy_output_posDx_UNDEFINED_BEHAVIOR_DataFrame.pickle']
    for df, pickle_filename in zip(processed_dataframes, filenames):
        df.to_pickle(f'{pickle_filename}')
    check_empty_dataframes(input_posDx_output_negDy_UNDEFINED_BEHAVIOR_DataFrame, 
                           input_negDy_output_posDx_UNDEFINED_BEHAVIOR_DataFrame)
    return(None)


# %%
def filter_dataframe_by_maximum_error(
    dataframe_to_filter: pd.DataFrame,
    input_name: str = 'posDx',
    output_name: str = 'negDy'
    ) -> pd.DataFrame:
    """
    ### Filters a multi-dimensional Pandas DataFrame to select the rows with the highest error value for a specified input-output pair, based on specified grouping columns. 

    ## Parameters:
    | Parameter Name        | Type           | Description                                            |
    |:----------------------|:---------------|:-------------------------------------------------------|
    | `dataframe_to_filter` | `pd.DataFrame` | A Pandas DataFrame containing the data to be filtered. |
    | `input_name`          | `str`          | Either 'posDx' or 'negDy', depending on the dataset.   |
    | `output_name`         | `str`          | Either 'posDx' or 'negDy', depending on the dataset.   |

    ## Returns:
    | Return name          | Type           | Description                                                                                                                                     |
    |:---------------------|:---------------|:------------------------------------------------------------------------------------------------------------------------------------------------|
    | `filtered_dataframe` | `pd.DataFrame` | A Pandas DataFrame containing only the rows with the highest error values for each unique set of coordinates in the specified grouping columns. |

    ## Examples:
    >>> filter_dataframe_by_maximum_error(input_posDx_output_negDy_NUMERIC_ERRORS_DataFrame, input_name = 'posDx', output_name = 'negDy')
    ...
    >>> filter_dataframe_by_maximum_error(input_negDy_output_posDx_NUMERIC_ERRORS_DataFrame, input_name = 'negDy', output_name = 'posDx')
    ...

    ## Notes:
    - If there are multiple rows with the same highest error value, the row with the highest input amount is returned. 
    - Rows with a zero or negative zero error value are removed.
    """
    columns_to_group_by = ['S precise (Decimal)', 'y intercept (int)', 'B precise (Decimal)']
    columns_to_sort_by = [f'error in output {output_name} (Decimal)', f'input {input_name} (int)']
    grouped_dataframe = dataframe_to_filter.sort_values(columns_to_sort_by, ascending = False).groupby(columns_to_group_by)
    max_error_indices = grouped_dataframe.apply(lambda x: x.index[0])
    filtered_dataframe = dataframe_to_filter.loc[max_error_indices]
    return(filtered_dataframe)


# %%
def filter_dataframe_by_zero_error(
    dataframe_to_filter: pd.DataFrame,
    input_name: str = 'posDx',
    output_name: str = 'negDy'
    ) -> pd.DataFrame:
    """
    ### Filters a multi-dimensional Pandas DataFrame to select the rows with zero error values for a specified input-output pair, based on specified grouping columns. 

    ## Parameters:
    | Parameter Name        | Type           | Description                                            |
    |:----------------------|:---------------|:-------------------------------------------------------|
    | `dataframe_to_filter` | `pd.DataFrame` | A Pandas DataFrame containing the data to be filtered. |
    | `input_name`          | `str`          | Either 'posDx' or 'negDy', depending on the dataset.   |
    | `output_name`         | `str`          | Either 'posDx' or 'negDy', depending on the dataset.   |

    ## Returns:
    | Return name          | Type           | Description                                                                                                                              |
    |:---------------------|:---------------|:-----------------------------------------------------------------------------------------------------------------------------------------|
    | `filtered_dataframe` | `pd.DataFrame` | A Pandas DataFrame containing only the rows with zero error values for each unique set of coordinates in the specified grouping columns. |

    ## Examples:
    >>> filter_dataframe_by_zero_error(input_posDx_output_negDy_NUMERIC_ERRORS_DataFrame, input_name = 'posDx', output_name = 'negDy')
    ...
    >>> filter_dataframe_by_zero_error(input_negDy_output_posDx_NUMERIC_ERRORS_DataFrame, input_name = 'negDy', output_name = 'posDx')
    ...

    ## Notes:
    - If there are multiple rows with zero error values, the row with the highest input amount is returned.
    """
    columns_to_group_by = ['S precise (Decimal)', 'y intercept (int)', 'B precise (Decimal)']
    zero_error_df = dataframe_to_filter[dataframe_to_filter[f'error in output {output_name} (Decimal)'] == 0]
    sorted_zero_error_df = zero_error_df.sort_values([f'input {input_name} (int)'], ascending=False)
    grouped_dataframe = sorted_zero_error_df.groupby(columns_to_group_by)
    filtered_dataframe = grouped_dataframe.first().reset_index()
    return(filtered_dataframe)


# %%
def filter_dataframe_by_maximum_input_for_middle_y(
    dataframe_to_filter: pd.DataFrame,
    input_name: str = 'posDx',
    output_name: str = 'negDy'
    ) -> pd.DataFrame:
    """
    ### Filters a multi-dimensional Pandas DataFrame to select the rows with the highest value of 'input {input_name} (int)' for the middle value of 'y (int)' for each unique set of coordinates in 'S precise (Decimal)', 'y intercept (int)', 'B precise (Decimal)'.

    ## Parameters:
    | Parameter Name        | Type           | Description                                            |
    |:----------------------|:---------------|:-------------------------------------------------------|
    | `dataframe_to_filter` | `pd.DataFrame` | A Pandas DataFrame containing the data to be filtered. |
    | `input_name`          | `str`          | Either 'posDx' or 'negDy', depending on the dataset.   |

    ## Returns:
    | Return name          | Type           | Description                                                                                                                                                                                                                            |
    |:---------------------|:---------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `filtered_dataframe` | `pd.DataFrame` | A Pandas DataFrame containing only the rows with the highest 'input {input_name} (int)' values for the middle 'y (int)' value for each unique set of coordinates in 'S precise (Decimal)', 'y intercept (int)', 'B precise (Decimal)'. |

    ## Examples:
    >>> filter_dataframe_by_maximum_input_for_middle_y(my_dataframe, 
                                                       input_name = 'posDx',
                                                       output_name = 'negDy')
    ...
    """
    columns_to_group_by = ['S precise (Decimal)', 'y intercept (int)', 'B precise (Decimal)']
    grouped_dataframe = dataframe_to_filter.groupby(columns_to_group_by)
    filtered_rows = []
    for group_name, group_data in grouped_dataframe:
        middle_y_value = group_data['y (int)'].median()
        middle_y_data = group_data[group_data['y (int)'] == middle_y_value]
        if not middle_y_data.empty:
            max_input_value = middle_y_data[f'input {input_name} (int)'].max()
            max_input_row = middle_y_data[middle_y_data[f'input {input_name} (int)'] == max_input_value].iloc[0]
            filtered_rows.append(max_input_row)
    filtered_dataframe = pd.concat(filtered_rows, axis = 1).T
    return(filtered_dataframe)


# %%
def scale_dataframe(
    dataframe_to_scale: pd.DataFrame
    ) -> pd.DataFrame:
    """
    ### Scales up the 'B precise (Decimal)' and 'S precise (Decimal)' columns in a Pandas DataFrame by 2 raised to the specified scaling factor. 

    ## Parameters:
    | Parameter Name       | Type           | Description                      |
    |:---------------------|:---------------|:---------------------------------|
    | `dataframe_to_scale` | `pd.DataFrame` | The input DataFrame to scale up. |

    ## Returns:
    | Return name        | Type           | Description                                       |
    |:-------------------|:---------------|:--------------------------------------------------|
    | `scaled_dataframe` | `pd.DataFrame` | The scaled-up DataFrame with the renamed columns. |

    ## Notes:
    - Renames the columns to 'B scaled up' and 'S scaled up'.
    """
    global SCALING_FACTOR
    scaled_dataframe = dataframe_to_scale.copy()
    scaled_dataframe[['B precise (Decimal)', 'S precise (Decimal)']] *= 2**SCALING_FACTOR
    scaled_dataframe.rename(columns={'B precise (Decimal)': 'B scaled up', 'S precise (Decimal)': 'S scaled up'}, inplace = True)
    return(scaled_dataframe)


# %%
def reduce_density(
    dataframe_to_reduce: pd.DataFrame,
    output_name: str = 'negDy',
    reduce_all_density: Union[int, bool] = False,
    reduce_zero_density: Union[int, bool] = 50000,
    reduce_non_zero_density: Union[int, bool] = 50000
    ) -> pd.DataFrame:
    """
    ### reduce_density reduces the density of a pandas DataFrame by randomly sampling a subset of the rows based on the specified criteria.

    ## Parameters:
    | Parameter names           | Parameter Types    | Parameter Descriptions                                                                                                                                                                                                             |
    |:--------------------------|:-------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `dataframe_to_reduce`     | `pd.DataFrame`     | The DataFrame to reduce.                                                                                                                                                                                                           |
    | `output_name`             | `str`              | The name of the output column to use for filtering. Defaults to 'negDy'.                                                                                                                                                           |
    | `reduce_all_density`      | `Union[int, bool]` | If set to an integer, this specifies the total number of rows to reduce to. If set to True, this reduces all rows in the DataFrame. Defaults to False.                                                                             |
    | `reduce_zero_density`     | `Union[int, bool]` | If set to an integer, this specifies the number of rows to reduce for which the error in the output column specified by `output_name` is zero. If set to `True`, this reduces all rows with zero error. Defaults to 50000.         |
    | `reduce_non_zero_density` | `Union[int, bool]` | If set to an integer, this specifies the number of rows to reduce for which the error in the output column specified by `output_name` is non-zero. If set to `True`, this reduces all rows with non-zero error. Defaults to 50000. |

    ## Returns:
    | Return names        | Return Type    | Return Descriptions    |
    |:--------------------|:---------------|:-----------------------|
    | `reduced_dataframe` | `pd.DataFrame` | The reduced DataFrame. |

    ## Examples:
    >>> reduced_dataframe = reduce_density(input_posDx_output_negDy_NUMERIC_ERRORS_DataFrame, 
                                           output_name = 'negDy', 
                                           reduce_all_density = False, 
                                           reduce_zero_density = 50000, 
                                           reduce_non_zero_density = 50000)
    ...
    >>> reduced_dataframe = reduce_density(input_negDy_output_posDx_NUMERIC_ERRORS_DataFrame, 
                                           output_name = 'posDx', 
                                           reduce_all_density = False, 
                                           reduce_zero_density = 50000, 
                                           reduce_non_zero_density = 50000)
    ...
    >>> reduced_dataframe = reduce_density(input_negDy_output_posDx_INFINITY_ERRORS_DataFrame, 
                                           output_name = 'posDx', 
                                           reduce_all_density = 50000, 
                                           reduce_zero_density = False, 
                                           reduce_non_zero_density = False)
    ...
    """    
    if reduce_all_density:
        reduce_all_density = min(reduce_all_density, len(dataframe_to_reduce))
        reduced_dataframe = dataframe_to_reduce.sample(n = reduce_all_density)
    
    else:
        zero_values_df = dataframe_to_reduce[dataframe_to_reduce[f'error in output {output_name} (Decimal)'] == 0]
        reduce_zero_density = min(reduce_zero_density, len(zero_values_df))
        reduced_zero_values_df = zero_values_df.sample(n = reduce_zero_density)
        
        non_zero_values_df = dataframe_to_reduce[dataframe_to_reduce[f'error in output {output_name} (Decimal)'] != 0]
        reduce_non_zero_density = min(reduce_non_zero_density, len(non_zero_values_df))
        reduced_non_zero_values_df = non_zero_values_df.sample(n = reduce_non_zero_density)
        
        reduced_dataframe = pd.concat([reduced_zero_values_df, reduced_non_zero_values_df])
    return(reduced_dataframe)


# %%
def get_color_dimension(
    data_point: Union[int, Decimal], 
    error_type: str
    ) -> float:
    """
    ### Computes the color dimension for a data point, based on the error type.

    ## Parameters:
    | Parameter Name   | Type                  | Description                                                                          |
    |:-----------------|:----------------------|:-------------------------------------------------------------------------------------|
    | `data_point`     | `Union[int, Decimal]` | The value to compute the color dimension for.                                        |
    | `error_type`     | `str`                 | The error type to use for computing the color dimension, either 'maximum' or 'zero'. |

    ## Returns:
    | Return name        | Type    | Description                   |
    |:-------------------|:--------|:------------------------------|
    | `log10_data_point` | `float` | The computed color dimension. |

    ## Examples:
    >>> get_color_dimension(0, 'maximum')
    -40.0
    >>> get_color_dimension(1.23, 'zero')
    0.08990511143939806
    """
    if error_type in ['maximum', 'maximum_input_at_middle_y']:
        log10_data_point = float(Decimal(data_point).log10()) if data_point > 0 else float(-40)
    elif error_type == 'zero':
        log10_data_point = float(Decimal(data_point).log10())
    return(log10_data_point)


# %%
def calculate_liquidity_wei_log10(
    liquidity_amount: Decimal,
    decimals: Decimal,
    price_USD: Decimal,
    ) -> float:
    """
    ### Calculates the logarithmic decimal representation of the given liquidity amount in wei, according to the token's decimality.
    
    ## Parameters
    | Parameter Name     | Type      | Description                           |
    |:-------------------|:----------|:--------------------------------------|
    | `liquidity_amount` | `Decimal` | The liquidity amount in units of USD. |
    | `decimals`         | `Decimal` | The decimality of the token.          |
    | `price_USD`        | `Decimal` | The price of the token in USD.        |
    
    ## Returns
    | Return Name           | Type    | Description                                                                                                       |
    |:----------------------|:--------|:------------------------------------------------------------------------------------------------------------------|
    | `liquidity_wei_log10` | `float` | The logarithmic decimal representation of the given liquidity amount in wei, according to the token's decimality. |
    
    """
    liquidity_wei_log10 = float((liquidity_amount*Decimal(10)**decimals/price_USD).log10())
    return(liquidity_wei_log10)


# %%
def calculate_min_max_liquidity_wei_log10(
    decimals_and_prices_USD: Dict[str, Dict[str, Union[int, float]]],
    min_max_liquidity_USD: List[int] = [500, 5_000_000],
    ) -> List[List[float]]:
    """
    ### Calculates the logarithmic decimal representation of the minimum and maximum liquidity amounts in wei for two tokens.
    
    ## Parameters
    | Parameter Name                     | Type                                        | Description                                                                                                                           |
    |:-----------------------------------|:--------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------|
    | `decimals_and_prices_USD`          | `Dict[str, Dict[str, Union[int, float]]]`   | A dictionary containing the token symbols as keys and another dictionary containing the token's `decimals` and `price_USD` as values. |
    | `min_max_liquidity`                | `List[int]`                                 | A list containing the minimum and maximum USD equivalent liquidity amounts to calculate. Defaults to `[500, 5_000_000]`.              |
    
    ## Parameter Dictionaries:
    ### Top Level:
    | Key   | Key Type   | Value                                                                                                  | Value Type                       |
    |:------|:-----------|:-------------------------------------------------------------------------------------------------------|:---------------------------------|
    | RISK  | `str`      | A dictionary containing the decimality and either the original or augmented price of RISK.             | `Dict[str, Union[int, Decimal]]` |

    #### OR
    | Key   | Key Type   | Value                                                                                                  | Value Type                       |
    |:------|:-----------|:-------------------------------------------------------------------------------------------------------|:---------------------------------|
    | CASH  | `str`      | A dictionary containing the decimality and either the original or augmented price of RISK.             | `Dict[str, Union[int, Decimal]]` |

    
    ### Bottom level
    | Key       | Key Type   | Value                                                      | Value Type   |
    |:----------|:-----------|:-----------------------------------------------------------|:-------------|
    | decimals  | `str`      | The Decimality of the CASH token.                          | `int`        |
    | price_USD | `str`      | The original or augmented price of the CASH token.         | `Decimal`    |
    #### OR
    | Key       | Key Type   | Value                                                      | Value Type   |
    |:----------|:-----------|:-----------------------------------------------------------|:-------------|
    | decimals  | `str`      | The Decimality of the RISK token.                          | `int`        |
    | price_USD | `str`      | The original or augmented price of the RISK token.         | `Decimal`    |

    ## Returns
    | Return Name                   | Type           | Description                                                                                                                            |
    |:------------------------------|:---------------|:---------------------------------------------------------------------------------------------------------------------------------------|
    | `min_max_liquidity_wei_log10` | `List[float]`  | A list of lists containing the minimum and maximum logarithmic decimal representations of the liquidity amounts in wei for each token. |
    
    ## Uses the following functions:
    | Function                        | Type       | Description                                                                             |
    |:--------------------------------|:-----------|:----------------------------------------------------------------------------------------|
    | `calculate_liquidity_wei_log10` | `function` | Calculates the logarithmic decimal representation of the given liquidity amount in wei. |
    
    ## Notes:
    - This function is called as part of a permutation method. 
    - The elaborate approach is a first attempt to coordinate the processing of the price and decimality inputs, with the other dimensions they will be plotted against. 
    - In each call of this function, the token identity is either RISK or CASH, exclusively. 
    - In each call of this function, the `price_USD` is either its original input value, or its augmented value, exclusively. 
    """
    min_max_liquidity_wei_log10 = [calculate_liquidity_wei_log10(
                                   Decimal(liquidity_amount),
                                   Decimal(decimals_and_prices_USD[token_symbol]['decimals']),
                                   Decimal(decimals_and_prices_USD[token_symbol]['price_USD']))
                                   for liquidity_amount in min_max_liquidity_USD
                                   for token_symbol in decimals_and_prices_USD.keys()]
    return(min_max_liquidity_wei_log10)


# %%
def calculate_B_scaled_up_log10(
    decimals_and_prices_USD: Dict[str, Dict[str, Union[int, Decimal]]]
    ) -> List[float]:
    """
    ### Calculates the `B` value that is used in the bonding curve formula. The `B` value is scaled up by the `SCALING_FACTOR`, then the result is taken as its base-10 logarithm.
    
    ## Parameters:
    | Parameter Name                   | Type                                        | Description                                                                         |
    |:---------------------------------|:--------------------------------------------|:------------------------------------------------------------------------------------|
    | decimals_and_prices_USD          | `Dict[str, Dict[str, Union[int, Decimal]]]` | A dictionary containing information about each token's decimality and price in USD. |
    
    ## Returns:
    | Return Name       | Type          | Description                                                                                                    |
    |:------------------|:--------------|:---------------------------------------------------------------------------------------------------------------|
    | B_scaled_up_log10 | `List[float]` | A list containing the logarithmic decimal representation of the curve constant `B` for each token in the pair. |
    """
    global SCALING_FACTOR
    B_scaled_up_log10 = [float((Decimal(2)**Decimal(SCALING_FACTOR)*Decimal.sqrt(Decimal(10)**(
                        + Decimal(decimals_and_prices_USD[token]['decimals']) 
                        - Decimal(decimals_and_prices_USD[other_token]['decimals']) 
                        - Decimal((decimals_and_prices_USD[token]['price_USD']/decimals_and_prices_USD[other_token]['price_USD']).log10())))).log10())
                        for token, other_token in permutations(decimals_and_prices_USD.keys(), 2)]
    return(B_scaled_up_log10)


# %%
def augment_prism_price_ranges(
    RISK_decimal: int,
    RISK_price_USD: Decimal,
    CASH_decimal: int,
    CASH_price_USD: Decimal,
    price_range_multiplier_log10: int
    ) -> Tuple[Dict[str, Dict[str, Union[int, Decimal]]]]:
    """
    ### Constructs a pair of dictionaries with modified prices, representing the two extremes of the input price ranges.

    ## Parameters:
    | Parameter Name               | Type            | Description                                                                                                                |
    |:-----------------------------|:----------------|:---------------------------------------------------------------------------------------------------------------------------|
    | RISK_decimal                 | `int`           | The number of decimal places for the RISK token.                                                                           |
    | RISK_price_USD               | `Decimal`       | The USD price of 1 unit of the RISK token.                                                                                 |
    | CASH_decimal                 | `int`           | The number of decimal places for the CASH token.                                                                           |
    | CASH_price_USD               | `Decimal`       | The USD price of 1 unit of the CASH token.                                                                                 |
    | price_range_multiplier_log10 | `int`           | The log10 of the amount to multiply the 'price_USD' values of 'RISK' and 'CASH' values to augment their price, separately. |

    ## Returns:
    | Return name                 | Type                                               | Description                                                                                                |
    |:----------------------------|:---------------------------------------------------|:-----------------------------------------------------------------------------------------------------------|
    | `decimals_and_prices_USD_A` | `Dict[str, Dict[str, Union[int, Decimal]]]`        | A dictionary with the 'RISK' price augmented by `10**price_range_multiplier_log10`.                        |
    | `decimals_and_prices_USD_B` | `Dict[str, Dict[str, Union[int, Decimal]]]`        | A dictionary with the 'CASH' price augmented by `10**price_range_multiplier_log10`.                        |
    |                             | `Tuple[Dict[str, Dict[str, Union[int, Decimal]]]]` | A tuple of decimals_and_prices_USD_A and decimals_and_prices_USD_B, in that order.                         |
    
    ## Return Dictionaries:
    ### Top Level:
    | Key   | Key Type   | Value                                                               | Value Type                       |
    |:------|:-----------|:--------------------------------------------------------------------|:---------------------------------|
    | RISK  | `str`      | A dictionary containing the decimality and augmented price of RISK. | `Dict[str, Union[int, Decimal]]` |
    |-------|------------|---------------------------------------------------------------------|----------------------------------|
    | CASH  | `str`      | A dictionary containing the decimality and original price of CASH.  | `Dict[str, Union[int, Decimal]]` |
    |-------|------------|---------------------------------------------------------------------|----------------------------------|
    | RISK  | `str`      | A dictionary containing the decimality and original price of RISK.  | `Dict[str, Union[int, Decimal]]` |
    |-------|------------|---------------------------------------------------------------------|----------------------------------|
    | CASH  | `str`      | A dictionary containing the decimality and augmented price of CASH. | `Dict[str, Union[int, Decimal]]` |
    
    ### Bottom level
    | Key       | Key Type   | Value                             | Value Type   |
    |:----------|:-----------|:----------------------------------|:-------------|
    | decimals  | `str`      | The Decimality of the RISK token. | `int`        |
    | price_USD | `str`      | The augmented price of RISK       | `Decimal`    |
    |-----------|------------|-----------------------------------|--------------|
    | decimals  | `str`      | The Decimality of the CASH token. | `int`        |
    | price_USD | `str`      | The original input price of CASH  | `Decimal`    |
    |-----------|------------|-----------------------------------|--------------|
    | decimals  | `str`      | The Decimality of the RISK token. | `int`        |
    | price_USD | `str`      | The original input price of RISK  | `Decimal`    |
    |-----------|------------|-----------------------------------|--------------|
    | decimals  | `str`      | The Decimality of the CASH token. | `int`        |
    | price_USD | `str`      | The augmented price of CASH       | `Decimal`    |
    
    ## Example:
    >>> RISK_decimal = 18
    >>> RISK_price_USD = Decimal('0.00001')
    >>> CASH_decimal = 8
    >>> CASH_price_USD = Decimal('100_000')
    >>> price_range_multiplier_log10 = 4
    >>> decimals_and_prices_USD_A, decimals_and_prices_USD_B = augment_price_ranges(RISK_decimal, RISK_price_USD, CASH_decimal, CASH_price_USD, price_range_multiplier_log10)
    >>> print(decimals_and_prices_USD_A)
    {'RISK': {'decimals': 18, 'price_USD': Decimal('0.10000')}, 'CASH': {'decimals': 8, 'price_USD': Decimal('100000')}}
    >>> print(decimals_and_prices_USD_A)
    {'RISK': {'decimals': 18, 'price_USD': Decimal('0.00001')}, 'CASH': {'decimals': 8, 'price_USD': Decimal('1000000000')}}

    ## Notes
    - The function constructs two dictionaries with the 'price_USD' value of either the RISK or the CASH token augmented by `10**price_range_multiplier_log10`.
    - The first dictionary (`decimals_and_prices_USD_A`) has the 'RISK' token price augmented, and the second dictionary (`decimals_and_prices_USD_B`) has the 'CASH' token price augmented.
    - A generator expression is used to produce these dictionaries. The expression yields one dictionary with the 'RISK' token price augmented, and then yields another dictionary with the 'CASH' token price augmented.
    """
    decimals_and_prices_USD_A, decimals_and_prices_USD_B = (
        {'RISK': {'decimals': RISK_decimal, 'price_USD': price_a},
        'CASH': {'decimals': CASH_decimal, 'price_USD': price_b}}
        for price_a, price_b in [(RISK_price_USD*Decimal('10')**Decimal(price_range_multiplier_log10), CASH_price_USD),
                                (RISK_price_USD, CASH_price_USD*Decimal('10')**Decimal(price_range_multiplier_log10))])
    return(decimals_and_prices_USD_A, decimals_and_prices_USD_B)


# %%
def calculate_B_scaled_up_log10_helper(
    decimals_and_prices_USD_A: Dict[str, Dict[str, Union[int, Decimal]]], 
    decimals_and_prices_USD_B: Dict[str, Dict[str, Union[int, Decimal]]]
    ) -> List[List[float]]:
    """
    ### Calculates the `B_scaled_up` value for 'RISK' and 'CASH' for two sets of token data.

    ## Parameters:
    | Parameter Name              | Type                                        | Description                                                                                                                           |
    |:----------------------------|:--------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------|
    | `decimals_and_prices_USD_A` | `Dict[str, Dict[str, Union[int, Decimal]]]` | A dictionary containing the token symbols as keys and another dictionary containing the token's `decimals` and `price_USD` as values. |
    | `decimals_and_prices_USD_B` | `Dict[str, Dict[str, Union[int, Decimal]]]` | A dictionary containing the token symbols as keys and another dictionary containing the token's `decimals` and `price_USD` as values. |

    ## Parameter Dictionaries:
    ### Top Level:
    | Key   | Key Type   | Value                                                               | Value Type                       |
    |:------|:-----------|:--------------------------------------------------------------------|:---------------------------------|
    | RISK  | `str`      | A dictionary containing the decimality and augmented price of RISK. | `Dict[str, Union[int, Decimal]]` |
    |-------|------------|---------------------------------------------------------------------|----------------------------------|
    | CASH  | `str`      | A dictionary containing the decimality and original price of CASH.  | `Dict[str, Union[int, Decimal]]` |
    |-------|------------|---------------------------------------------------------------------|----------------------------------|
    | RISK  | `str`      | A dictionary containing the decimality and original price of RISK.  | `Dict[str, Union[int, Decimal]]` |
    |-------|------------|---------------------------------------------------------------------|----------------------------------|
    | CASH  | `str`      | A dictionary containing the decimality and augmented price of CASH. | `Dict[str, Union[int, Decimal]]` |
    
    ### Bottom level
    | Key       | Key Type   | Value                             | Value Type   |
    |:----------|:-----------|:----------------------------------|:-------------|
    | decimals  | `str`      | The Decimality of the RISK token. | `int`        |
    | price_USD | `str`      | The augmented price of RISK       | `Decimal`    |
    |-----------|------------|-----------------------------------|--------------|
    | decimals  | `str`      | The Decimality of the CASH token. | `int`        |
    | price_USD | `str`      | The original input price of CASH  | `Decimal`    |
    |-----------|------------|-----------------------------------|--------------|
    | decimals  | `str`      | The Decimality of the RISK token. | `int`        |
    | price_USD | `str`      | The original input price of RISK  | `Decimal`    |
    |-----------|------------|-----------------------------------|--------------|
    | decimals  | `str`      | The Decimality of the CASH token. | `int`        |
    | price_USD | `str`      | The augmented price of CASH       | `Decimal`    |

    ## Returns:
    | Return name               | Type                | Description                                                                                                                                                                                    |
    |:--------------------------|:--------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `B_scaled_up_log10_list`  | `List[List[float]]` | A list of two `float` values, corresponding to `B_scaled_up_log10` for `RISK` and `CASH` tokens in the dictionaries `decimals_and_prices_USD_A` and `decimals_and_prices_USD_B`, in that order.|

    ## Example:
    >>> decimals_and_prices_USD_A = {'RISK': {'decimals': 18, 'price_USD': Decimal('0.10000')}, 'CASH': {'decimals': 8, 'price_USD': Decimal('100000')}}
    >>> decimals_and_prices_USD_B = {'RISK': {'decimals': 18, 'price_USD': Decimal('0.00001')}, 'CASH': {'decimals': 8, 'price_USD': Decimal('1000000000')}}
    >>> calculate_B_scaled_up_log10_helper(decimals_and_prices_USD_A, decimals_and_prices_USD_B)
    [[22.449439791871097, 26.449439791871097], [6.4494397918710975, 2.4494397918710975]]

    ## Notes
    - The function calculates `B_scaled_up` for both sets of token data and returns a tuple of two lists. 
    - The two lists contain `B_scaled_up_log10` values for 'RISK' and 'CASH' tokens in the two dictionaries, in that order.
    - The lists are not sorted; values can be ascending or descending.
    
    ## Uses the following functions:
    | Function                      | Type       | Description                                                  |
    |:------------------------------|:-----------|:-------------------------------------------------------------|
    | `calculate_B_scaled_up_log10` | `function` | Calculates the `B_scaled_up` value for the given token data. |
    """
    B_scaled_up_log10_A = calculate_B_scaled_up_log10(decimals_and_prices_USD_A)
    B_scaled_up_log10_B = calculate_B_scaled_up_log10(decimals_and_prices_USD_B)
    return([([B_scaled_up_log10_A[0], B_scaled_up_log10_B[0]]), 
            ([B_scaled_up_log10_A[1], B_scaled_up_log10_B[1]])])


# %%
def calculate_min_max_liquidity_wei_log10_helper(
    decimals_and_prices_USD_A: Dict[str, Dict[str, Union[int, Decimal]]], 
    decimals_and_prices_USD_B: Dict[str, Dict[str, Union[int, Decimal]]], 
    min_max_liquidity_USD: List[Decimal]
    ) -> List[List[List[float]]]:
    """
    ### Calculates the log10 values of minimum and maximum liquidity, for both RISK and CASH tokens, for two sets of token data.

    ## Parameters:
    | Parameter Name                   | Type                                        | Description                                                                                                                           |
    |:---------------------------------|:--------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------|
    | `decimals_and_prices_USD_A`      | `Dict[str, Dict[str, Union[int, Decimal]]]` | A dictionary containing the token symbols as keys and another dictionary containing the token's `decimals` and `price_USD` as values. |
    | `decimals_and_prices_USD_B`      | `Dict[str, Dict[str, Union[int, Decimal]]]` | A dictionary containing the token symbols as keys and another dictionary containing the token's `decimals` and `price_USD` as values. |
    | `min_max_liquidity_USD`          | `List[Decimal]`                             | A list containing two `Decimal` values, corresponding to the minimum and maximum liquidity in USD, respectively.                      |

    ## Parameter Dictionaries:
    ### Top Level:
    | Key   | Key Type   | Value                                                               | Value Type                       |
    |:------|:-----------|:--------------------------------------------------------------------|:---------------------------------|
    | RISK  | `str`      | A dictionary containing the decimality and augmented price of RISK. | `Dict[str, Union[int, Decimal]]` |
    |-------|------------|---------------------------------------------------------------------|----------------------------------|
    | CASH  | `str`      | A dictionary containing the decimality and original price of CASH.  | `Dict[str, Union[int, Decimal]]` |
    |-------|------------|---------------------------------------------------------------------|----------------------------------|
    | RISK  | `str`      | A dictionary containing the decimality and original price of RISK.  | `Dict[str, Union[int, Decimal]]` |
    |-------|------------|---------------------------------------------------------------------|----------------------------------|
    | CASH  | `str`      | A dictionary containing the decimality and augmented price of CASH. | `Dict[str, Union[int, Decimal]]` |
    
    ### Bottom level
    | Key       | Key Type   | Value                             | Value Type   |
    |:----------|:-----------|:----------------------------------|:-------------|
    | decimals  | `str`      | The Decimality of the RISK token. | `int`        |
    | price_USD | `str`      | The augmented price of RISK       | `Decimal`    |
    |-----------|------------|-----------------------------------|--------------|
    | decimals  | `str`      | The Decimality of the CASH token. | `int`        |
    | price_USD | `str`      | The original input price of CASH  | `Decimal`    |
    |-----------|------------|-----------------------------------|--------------|
    | decimals  | `str`      | The Decimality of the RISK token. | `int`        |
    | price_USD | `str`      | The original input price of RISK  | `Decimal`    |
    |-----------|------------|-----------------------------------|--------------|
    | decimals  | `str`      | The Decimality of the CASH token. | `int`        |
    | price_USD | `str`      | The augmented price of CASH       | `Decimal`    |

    ## Returns:
    | Return name                       | Type                      | Description                                                                                                                                                                          |
    |:----------------------------------|:--------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `log10_min_max_liquidity_list`    | `List[List[List[float]]]` | A list of two lists of `float` values, corresponding to the log10 values of minimum and maximum liquidity, for RISK and CASH tokens, respectively, in the two input dictionaries.  |

    ## Example:
    >>> decimals_and_prices_USD_A = {'RISK': {'decimals': 18, 'price_USD': Decimal('0.10000')}, 'CASH': {'decimals': 8, 'price_USD': Decimal('100000')}}
    >>> decimals_and_prices_USD_B = {'RISK': {'decimals': 18, 'price_USD': Decimal('0.00001')}, 'CASH': {'decimals': 8, 'price_USD': Decimal('1000000000')}}
    >>> min_max_liquidity_USD = [Decimal('500'), Decimal('5_000_000')]
    >>> calculate_min_max_liquidity_wei_log10_helper(decimals_and_prices_USD_A, decimals_and_prices_USD_B, min_max_liquidity_USD)
    [[[21.69897000433602, 25.69897000433602], 
      [25.69897000433602, 29.69897000433602]], 
     [[5.698970004336019, 9.698970004336019], 
      [1.6989700043360187, 5.698970004336019]]]

    ## Notes
    - The function calculates the log10 values of minimum and maximum liquidity for RISK and CASH tokens in two dictionaries and returns a list of two lists.
    - The first list in the return value contains the log10 values of minimum and maximum liquidity for RISK tokens, corresponding to the values in the two input dictionaries. Values can be ascending or descending.
    - The second list in the return value contains the log10 values of minimum and maximum liquidity for CASH tokens, corresponding to the values in the two input dictionaries. Values can be ascending or descending.

    ## Uses the following functions:
    | Function                                | Type       | Description                                                                              |
    |:----------------------------------------|:-----------|:-----------------------------------------------------------------------------------------|
    | `calculate_min_max_liquidity_wei_log10` | `function` | Calculates the logarithmic decimal representation of the given liquidity amounts in wei. |
    """
    liquidity_A = calculate_min_max_liquidity_wei_log10(decimals_and_prices_USD_A, min_max_liquidity_USD)
    liquidity_B = calculate_min_max_liquidity_wei_log10(decimals_and_prices_USD_B, min_max_liquidity_USD)
    return([([[liquidity_A[0], liquidity_A[2]], [liquidity_B[0], liquidity_B[2]]]), 
            ([[liquidity_A[1], liquidity_A[3]], [liquidity_B[1], liquidity_B[3]]])])


# %%
def construct_vertices(
    B_scaled_up_log10_array: List[float], 
    min_max_liquidity_log10_array: List[List[float]],
    min_max_S_log10: List[int]
    ) -> List[List[Union[float, int]]]:
    
    """
    ### Constructs a list of vertices for a quadrangular prism using the given parameters.

    ## Parameters:
    | Parameter Name                   | Type                    | Description                                                                                                                               |
    |:---------------------------------|:------------------------|:------------------------------------------------------------------------------------------------------------------------------------------|
    | `B_scaled_up_log10_array`        | `List[float]`           | A list containing two `float` values, corresponding to the bounds of the `B` variable.                                                    |
    | `min_max_liquidity_log10_array`  | `List[List[float]]`     | A list of two lists of `float` values, corresponding to the minimum and maximum liquidity values for RISK and CASH tokens, respectively.  |
    | `min_max_S_log10`                | `List[int]`             | A list containing two `int` values, corresponding to the minimum and maximum `S` variable values, respectively.                           |

    ## Returns:
    | Return name                       | Type                            | Description                                                                                                                                                                          |
    |:----------------------------------|:--------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `vertices`                        | `List[List[Union[float, int]]]` | A list of eight lists, each containing three values: `B`, `S`, and liquidity for either the RISK or CASH token. The first and last vertices are opposite each other and the same for both RISK and CASH. The second and third vertices, and fourth and fifth vertices, are opposite each other and the same for RISK and CASH, respectively.

    ## Example:
    >>> B_scaled_up_log10_array = [22.449439791871097, 26.449439791871097]
    >>> min_max_liquidity_log10_array = [[21.69897000433602, 25.69897000433602], [25.69897000433602, 29.69897000433602]]
    >>> min_max_S_log10 = [-30, 30]
    >>> create_prism_vertices(B_scaled_up_log10_array, min_max_liquidity_log10_array, min_max_S_log10)
    [[22.449439791871097, -30, 21.69897000433602], 
     [22.449439791871097,  30, 21.69897000433602], 
     [26.449439791871097,  30, 25.69897000433602], 
     [26.449439791871097, -30, 25.69897000433602], 
     [22.449439791871097, -30, 25.69897000433602], 
     [22.449439791871097,  30, 25.69897000433602], 
     [26.449439791871097,  30, 29.69897000433602], 
     [26.449439791871097, -30, 29.69897000433602]]

    ## Notes:
    - The function constructs a list of vertices for a prism using the given parameters. 
    - Each vertex is a list of three values: `B`, `S`, and `y_int` (i.e 'liquidity'). 
    - The vertices are returned in a list containing eight sublists, each sublist representing the 3D coordinates of the corners of a quadrangular prism. 
    - The edges are defined by these vertex doublets: ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (5, 1), (6, 2), (7, 3), (4, 0))
    - The faces are defined by these vertex quadruplets: ((0, 1, 2, 3), (4, 5, 6, 7), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (0, 1, 5, 4))
    """
#                 x = B_scaled_up_log10    y = S_scaled_up_log10         z = y_int_log10
    vertices = [[B_scaled_up_log10_array[0], min_max_S_log10[0], min_max_liquidity_log10_array[0][0]],
                [B_scaled_up_log10_array[0], min_max_S_log10[1], min_max_liquidity_log10_array[0][0]],
                [B_scaled_up_log10_array[1], min_max_S_log10[1], min_max_liquidity_log10_array[1][0]],
                [B_scaled_up_log10_array[1], min_max_S_log10[0], min_max_liquidity_log10_array[1][0]],
                [B_scaled_up_log10_array[0], min_max_S_log10[0], min_max_liquidity_log10_array[0][1]],
                [B_scaled_up_log10_array[0], min_max_S_log10[1], min_max_liquidity_log10_array[0][1]],
                [B_scaled_up_log10_array[1], min_max_S_log10[1], min_max_liquidity_log10_array[1][1]],
                [B_scaled_up_log10_array[1], min_max_S_log10[0], min_max_liquidity_log10_array[1][1]]]
    return(vertices)


# %%
def format_number_with_percentage_or_dollar_sign(price: float = None, multiplier: int = None) -> str:
    """
    ### Formats a given number with a dollar sign or the appropriate number of zeros appended and returns a string with comma separation.

    ## Parameters:
    | Parameter Name   | Type   | Description                                                                                                                           |
    |:-----------------|:-------|:--------------------------------------------------------------------------------------------------------------------------------------|
    | `price`          | `float`| A floating-point number to format as a dollar amount, if less than 1; otherwise, `None`.                                              |
    | `multiplier`     | `int`  | The number of zeros to append to the number 100. Must be a non-negative integer. If `price` is not `None`, this parameter is ignored. |

    ## Returns:
    | Return Name       | Type    | Description                                                                     |
    |:------------------|:--------|:--------------------------------------------------------------------------------|
    | `formatted_value` | `str`   | A string containing the formatted number with a dollar sign or percentage sign. |

    ## Raises:
    | Exception                  | Description                                                         |
    |:---------------------------|:--------------------------------------------------------------------|
    | `ValueError`               | Raised when `multiplier` is negative.                               |
    | `TypeError`                | Raised when both `price` and `multiplier` are `None`.               |
    | `ValueError`               | Raised when `price` is not `None` and is less than or equal to 0.   |

    ## Examples:
    >>> format_number_with_percentage(price=0.00001)
    '0.00001$'
    >>> format_number_with_percentage(price=1.23)
    '$1.23'
    >>> format_number_with_percentage(multiplier=4)
    '100,000%'
    """
    if price is not None:
        if price <= 0:
            raise ValueError('`price` must be greater than 0.')
        formatted_value = f'${price}' if price < 1 else f'${price:,.2f}'
    elif multiplier is not None:
        if multiplier < 0:
            raise ValueError('`multiplier` must be non-negative.')
        percent_value = 100 * (10 ** multiplier)
        formatted_value = f'{percent_value:,.0f}%'
    else:
        raise TypeError('Either `price` or `multiplier` must be provided.')
    return (formatted_value)


# %%
def get_prism_annotations(
    RISK_asset: str = 'SHIB',
    RISK_decimal: int = 18,
    RISK_price_USD: Decimal = Decimal('0.00001'),
    CASH_asset: str = 'WBTC',
    CASH_decimal: int = 8,
    CASH_price_USD: Decimal = Decimal('100_000'),
    min_max_liquidity_USD: List[Decimal] = [Decimal('500'), Decimal('5_000_000')],
    price_range_multiplier_log10: int = 4
    ):
    """
    ### Generates annotation strings for two opposite prisms.

    ## Parameters:
    | Parameter Name                    | Type            | Description                                                                                                         |
    |:----------------------------------|:----------------|:--------------------------------------------------------------------------------------------------------------------|
    | `RISK_asset`                      | `str`           | The symbol of the RISK token.                                                                                       |
    | `RISK_decimal`                    | `int`           | The number of decimals for the RISK token.                                                                          |
    | `RISK_price_USD`                  | `Decimal`       | The USD price of the RISK token.                                                                                    |
    | `CASH_asset`                      | `str`           | The symbol of the CASH token.                                                                                       |
    | `CASH_decimal`                    | `int`           | The number of decimals for the CASH token.                                                                          |
    | `CASH_price_USD`                  | `Decimal`       | The USD price of the CASH token.                                                                                    |
    | `min_max_liquidity_USD`           | `List[Decimal]` | A list containing two `Decimal` values, corresponding to the minimum and maximum liquidity in USD, respectively.    |
    | `price_range_multiplier_log10`    | `int`           | The number of zeros to append to the number 100 for formatting percentage values. Must be a non-negative integer.   |

    ## Returns:
    | Return Name           | Type     | Description                                               |
    |:----------------------|:---------|:----------------------------------------------------------|
    | `forwards_annotation` | `str`    | An annotation string for the first (RISK/CASH) prism.     |
    | `reverse_annotation`  | `str`    | An annotation string for the second (CASH/RISK) prism.    |

    ## Examples:
    >>> annotations = prism_annotations()
    >>> print(annotations[0])
    18 decimal token @ $0.00001
    -vs-
    8 decimal token @ $100,000.00
    +/- 1,000,000%
    ----
    top surface = $5,000,000.00 liquidity
    bottom surface = $500.00 liquidity
    reference case = SHIB/WBTC
    >>> print(annotations[1])
    8 decimal token @ $100,000.00
    -vs-
    18 decimal token @ $0.00001
    +/- 1,000,000%
    ----
    top surface = $5,000,000.00 liquidity
    bottom surface = $500.00 liquidity
    reference case = WBTC/SHIB
    
    ## Uses the following functions:
    | Function                                       | Type       | Description                                                                                              |
    |:-----------------------------------------------|:-----------|:---------------------------------------------------------------------------------------------------------|
    | `format_number_with_percentage_or_dollar_sign` | `function` | Formats a given number with a '$' or '%' sign or the appropriate number of zeros, with comma separation. |
    """
    # forwards_annotation = (
    #     f'\n \
    #     {RISK_decimal} decimal token @ {format_number_with_percentage_or_dollar_sign(price = RISK_price_USD)} \n \
    #     -vs- \n \
    #     {CASH_decimal} decimal token @ {format_number_with_percentage_or_dollar_sign(price = CASH_price_USD)}  \n \
    #     +/- {format_number_with_percentage_or_dollar_sign(multiplier = price_range_multiplier_log10)} \n \
    #     ---- \n \
    #     top surface = {format_number_with_percentage_or_dollar_sign(price = min_max_liquidity_USD[1])} liquidity \n \
    #     bottom surface = {format_number_with_percentage_or_dollar_sign(price = min_max_liquidity_USD[0])} liquidity \n \
    #     reference case = {RISK_asset}/{CASH_asset}'
    #     )
    # reverse_annotation = (
    #     f'\n \
    #     {CASH_decimal} decimal token @ {format_number_with_percentage_or_dollar_sign(price = CASH_price_USD)} \n \
    #     -vs- \n \
    #     {RISK_decimal} decimal token @ {format_number_with_percentage_or_dollar_sign(price = RISK_price_USD)}  \n \
    #     +/- {format_number_with_percentage_or_dollar_sign(multiplier = price_range_multiplier_log10)} \n \
    #     ---- \n \
    #     top surface = {format_number_with_percentage_or_dollar_sign(price = min_max_liquidity_USD[1])} liquidity \n \
    #     bottom surface = {format_number_with_percentage_or_dollar_sign(price = min_max_liquidity_USD[0])} liquidity \n \
    #     reference case = {CASH_asset}/{RISK_asset}'
    #     )
    forwards_annotation = f'\
        <br>{RISK_decimal} decimal token @ {format_number_with_percentage_or_dollar_sign(price = RISK_price_USD)}\
            <br>-vs-\
                <br>{CASH_decimal} decimal token @ {format_number_with_percentage_or_dollar_sign(price = CASH_price_USD)}\
                    <br>&#177;{format_number_with_percentage_or_dollar_sign(multiplier = price_range_multiplier_log10)}\
                        <br>----\
                            <br>top surface = {format_number_with_percentage_or_dollar_sign(price = min_max_liquidity_USD[1])} liquidity\
                                <br>bottom surface = {format_number_with_percentage_or_dollar_sign(price = min_max_liquidity_USD[0])} liquidity\
                                    <br>reference case = {RISK_asset}/{CASH_asset}'

    reverse_annotation = f'\
        <br>{CASH_decimal} decimal token @ {format_number_with_percentage_or_dollar_sign(price = CASH_price_USD)}\
            <br>-vs-\
                <br>{RISK_decimal} decimal token @ {format_number_with_percentage_or_dollar_sign(price = RISK_price_USD)}\
                    <br>&#177;{format_number_with_percentage_or_dollar_sign(multiplier = price_range_multiplier_log10)}\
                        <br>----\
                            <br>top surface = {format_number_with_percentage_or_dollar_sign(price = min_max_liquidity_USD[1])} liquidity\
                                <br>bottom surface = {format_number_with_percentage_or_dollar_sign(price = min_max_liquidity_USD[0])} liquidity\
                                    <br>reference case = {CASH_asset}/{RISK_asset}'
    return(forwards_annotation, reverse_annotation)


# %%
def annotate_prism(
    prism_annotaion: str,
    prism_vertices: List[List[Union[float, int]]],
    color_hexcode: str
    ):
    """
    ### Combines the prism annotation with its vertices in a dictionary.
    
    ## Parameters:
    | Parameter Name      | Type                            | Description                                                               |
    |:--------------------|:--------------------------------|:--------------------------------------------------------------------------|
    | `prism_annotaion`   | `str`                           | The annotation to add to the prism.                                       |
    | `prism_vertices`    | `List[List[Union[float, int]]]` | The vertices of the prism; each vertex is a list of three coordinates.    |

    ## Returns:
    | Return Name       | Type             | Description                                        |
    |:------------------|:-----------------|:---------------------------------------------------|
    | `annotated_prism` | `Dict[str, Any]` | A dictionary with the following keys, value pairs: |

    ## Return Dictionary:
    | Key        | Key Type   | Value                                                                                                                          | Value Type                      |
    |:-----------|:-----------|:-------------------------------------------------------------------------------------------------------------------------------|:--------------------------------|
    | annotation | `str`      | The annotation added to the prism, which describes its meaning with reference to a specific token pair                         | `str`                           |
    | vertices   | `str`      | The coordinates for the eight vertices of a quadrangular prism with dimensions of `B` (log10), `S` (log10) and `y_int` (log10) | `List[List[Union[float, int]]]` |
    | color      | `str`      | The hexcode for the color of the prism, as it will appear alongside the plotted errors data.                                   | `str`                           |

    """
    annotated_prism = {
        'annotation' : prism_annotaion,
        'vertices' : prism_vertices,
        'color' : color_hexcode
    }
    return(annotated_prism)


# %%
def get_annotated_prism_for_token_pair_of_interest(
    RISK_asset: str = 'SHIB',
    RISK_decimal: int = 18,
    RISK_price_USD: Decimal = Decimal('0.00001'),
    CASH_asset: str = 'WBTC',
    CASH_decimal: int = 8,
    CASH_price_USD: Decimal = Decimal('100_000'),
    min_max_liquidity_USD: List[Decimal] = [Decimal('500'), Decimal('5_000_000')],
    min_max_S_log10: List[int] = [-30 , 30],
    price_range_multiplier_log10: int = 4,
    color_hexcode = '#d86371'
    ) -> Tuple[Dict[str, Union[str, List[List[Union[float, int]]]]]]:
    """
    ### Constructs two prisms that represent the liquidity pool for a token pair of interest, which can be incorporated into the errors analysis visualizations.
    
    ## Parameters:
    | Parameter Name                 | Type            | Description                                                                                                                |
    |:-------------------------------|:----------------|:---------------------------------------------------------------------------------------------------------------------------|
    | `RISK_asset`                   | `str`           | The symbol of the RISK token.                                                                                              |
    | `RISK_decimal`                 | `int`           | The number of decimals for the RISK token.                                                                                 |
    | `RISK_price_USD`               | `Decimal`       | The USD price of the RISK token.                                                                                           |
    | `CASH_asset`                   | `str`           | The symbol of the CASH token.                                                                                              |
    | `CASH_decimal`                 | `int`           | The number of decimals for the CASH token.                                                                                 |
    | `CASH_price_USD`               | `Decimal`       | The USD price of the CASH token.                                                                                           |
    | `min_max_liquidity_USD`        | `List[Decimal]` | A list containing two `Decimal` values, corresponding to the minimum and maximum liquidity in USD, respectively.           |
    | `min_max_S_log10`              | `List[int]`     | A list containing two integers, corresponding to the minimum and maximum values for `S`.                                   |
    | `price_range_multiplier_log10` | `int`           | The log10 of the amount to multiply the 'price_USD' values of 'RISK' and 'CASH' values to augment their price, separately. |
    
    ## Returns:
    | Return Name   | Type                                                          | Description                                                                                  |
    |:--------------|:--------------------------------------------------------------|:---------------------------------------------------------------------------------------------|
    |               | `Tuple[Dict[str, Union[str, List[List[Union[float, int]]]]]]` | A tuple containing two dictionaries that represent the annotated prisms for each token pair. |
    
    ## Uses the following functions:
    | Function                                       | Type       | Description                                                                                                                                                                                 |
    |:-----------------------------------------------|:-----------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `get_prism_annotations`                        | `function` | Returns the annotations for the two prisms based on the token symbols and USD prices.                                                                                                       |
    | `augment_prism_price_ranges`                   | `function` | Augments the `price_USD` values of the two tokens by a specified multiplier.                                                                                                                |
    | `calculate_B_scaled_up_log10_helper`           | `function` | Calculates the log10 of the scaled-up `price_USD` value for each token.                                                                                                                     |
    | `calculate_min_max_liquidity_wei_log10_helper` | `function` | Calculates the log10 of the minimum and maximum liquidity for each token.                                                                                                                   |
    | `construct_vertices`                           | `function` | Constructs the vertices for a prism based on the scaled-up token prices, liquidity range, and the range for the dimension perpendicular to the plane of the liquidity and token price axes. |
    | `annotate_prism`                               | `function` | Returns a dictionary with an annotation and vertices of a prism.                                                                                                                            |
    """
    forwards_annotation, reverse_annotation = get_prism_annotations(RISK_asset = RISK_asset,
                                                                    RISK_decimal = RISK_decimal,
                                                                    RISK_price_USD = RISK_price_USD,
                                                                    CASH_asset = CASH_asset,
                                                                    CASH_decimal = CASH_decimal,
                                                                    CASH_price_USD = CASH_price_USD,
                                                                    min_max_liquidity_USD = min_max_liquidity_USD,
                                                                    price_range_multiplier_log10 = price_range_multiplier_log10)
    decimals_and_prices_USD_A, decimals_and_prices_USD_B = augment_prism_price_ranges(RISK_decimal, RISK_price_USD, CASH_decimal, CASH_price_USD, price_range_multiplier_log10)
    B_scaled_up_RISK_log10, B_scaled_up_CASH_log10 = calculate_B_scaled_up_log10_helper(decimals_and_prices_USD_A, decimals_and_prices_USD_B)
    min_max_RISK_liquidity_log10, min_max_CASH_liquidity_log10 = calculate_min_max_liquidity_wei_log10_helper(decimals_and_prices_USD_A, decimals_and_prices_USD_B, min_max_liquidity_USD)
    RISK_prism_vertices = construct_vertices(B_scaled_up_RISK_log10, min_max_RISK_liquidity_log10, min_max_S_log10)
    CASH_prism_vertices = construct_vertices(B_scaled_up_CASH_log10, min_max_CASH_liquidity_log10, min_max_S_log10)
    annotated_RISK_prism = annotate_prism(forwards_annotation, RISK_prism_vertices, color_hexcode)
    annotated_CASH_prism = annotate_prism(reverse_annotation, CASH_prism_vertices, color_hexcode)
    return(annotated_RISK_prism, annotated_CASH_prism)


# %%
PRISM_LIBRARY = [get_annotated_prism_for_token_pair_of_interest(RISK_asset = 'SHIB',
                                                                RISK_decimal = 18,
                                                                RISK_price_USD = Decimal('0.00001'),
                                                                CASH_asset = 'WBTC',
                                                                CASH_decimal = 8,
                                                                CASH_price_USD = Decimal('100_000'),
                                                                min_max_liquidity_USD = [Decimal('500'), Decimal('5_000_000')],
                                                                min_max_S_log10 = [-30 , 30],
                                                                price_range_multiplier_log10 = 4,
                                                                color_hexcode = '#ff7300'),
                 get_annotated_prism_for_token_pair_of_interest(RISK_asset = 'SHIB',
                                                                RISK_decimal = 18,
                                                                RISK_price_USD = Decimal('0.00001'),
                                                                CASH_asset = 'USDC',
                                                                CASH_decimal = 6,
                                                                CASH_price_USD = Decimal('1.00'),
                                                                min_max_liquidity_USD = [Decimal('500'), Decimal('5_000_000')],
                                                                min_max_S_log10 = [-30 , 30],
                                                                price_range_multiplier_log10 = 4,
                                                                color_hexcode = '#ff4300'),
                 get_annotated_prism_for_token_pair_of_interest(RISK_asset = 'SHIB',
                                                                RISK_decimal = 18,
                                                                RISK_price_USD = Decimal('0.00001'),
                                                                CASH_asset = 'DAI',
                                                                CASH_decimal = 18,
                                                                CASH_price_USD = Decimal('1.00'),
                                                                min_max_liquidity_USD = [Decimal('500'), Decimal('5_000_000')],
                                                                min_max_S_log10 = [-30 , 30],
                                                                price_range_multiplier_log10 = 4,
                                                                color_hexcode = '#ff0000'),
                 get_annotated_prism_for_token_pair_of_interest(RISK_asset = 'BNT',
                                                                RISK_decimal = 18,
                                                                RISK_price_USD = Decimal('0.10'),
                                                                CASH_asset = 'WBTC',
                                                                CASH_decimal = 8,
                                                                CASH_price_USD = Decimal('100_000'),
                                                                min_max_liquidity_USD = [Decimal('500'), Decimal('5_000_000')],
                                                                min_max_S_log10 = [-30 , 30],
                                                                price_range_multiplier_log10 = 4,
                                                                color_hexcode = '#ff005f'),
                get_annotated_prism_for_token_pair_of_interest(RISK_asset = 'BNT',
                                                               RISK_decimal = 18,
                                                               RISK_price_USD = Decimal('0.10'),
                                                               CASH_asset = 'USDC',
                                                               CASH_decimal = 6,
                                                               CASH_price_USD = Decimal('1.00'),
                                                               min_max_liquidity_USD = [Decimal('500'), Decimal('5_000_000')],
                                                               min_max_S_log10 = [-30 , 30],
                                                               price_range_multiplier_log10 = 4,
                                                               color_hexcode = '#ff00c4'),
                get_annotated_prism_for_token_pair_of_interest(RISK_asset = 'BNT',
                                                               RISK_decimal = 18,
                                                               RISK_price_USD = Decimal('0.10'),
                                                               CASH_asset = 'DAI',
                                                               CASH_decimal = 18,
                                                               CASH_price_USD = Decimal('1.00'),
                                                               min_max_liquidity_USD = [Decimal('500'), Decimal('5_000_000')],
                                                               min_max_S_log10 = [-30 , 30],
                                                               price_range_multiplier_log10 = 4,
                                                               color_hexcode = '#e300ff')]


# %%
def visualize_numeric_errors(
    dataframe_to_visualize: pd.DataFrame,
    filename: str = 'test_error_profiling',
    title: str = None,
    error_type: str = 'maximum',
    input_name: str = 'posDx',
    output_name: str = 'negDy',
    reduce_all_density: Union[int, bool] = False,
    reduce_zero_density: Union[int, bool] = 50000,
    reduce_non_zero_density: Union[int, bool] = 50000,
    show_fig: bool = False,
    reference_prisms: bool = False,
    ) -> None:
    """
    ### Creates a 3D scatter plot using Plotly Express to visualize the errors in a numeric dataset.

    ## Parameters:
    | Parameter names           | Parameter Types      | Parameter Descriptions                                                                                                                                                                                                                                                                                                                                                                                                                                          |
    |:--------------------------|:---------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `dataframe_to_visualize`  | `pd.DataFrame`       | The input DataFrame to be visualized.                                                                                                                                                                                                                                                                                                                                                                                                                           |
    | `filename`                | `str`                | The filename corresponding to the analysis being performed.                                                                                                                                                                                                                                                                                                                                                                                                     |
    | `title`                   | `str`                | The title of the plot. If None, the title will not be displayed. Defaults to None.                                                                                                                                                                                                                                                                                                                                                                              |
    | `error_type`              | `str`                | The type of error to visualize. Must be '`maximum`', '`zero`', or '`maximum_input_at_middle_y`'. If '`maximum`', the errors will be filtered based on the maximum error for the output_name column. If '`zero`', the errors will be filtered based on the error being zero for the input_name column. If '`maximum_input_at_middle_y`', the errors will be filtered based on the maximum input value for a specific y intercept value. Defaults to '`maximum`'. |
    | `input_name`              | `str`                | The name of the input column to use for filtering. Defaults to `posDx`.                                                                                                                                                                                                                                                                                                                                                                                         |
    | `output_name`             | `str`                | The name of the output column to use for filtering. Defaults to `negDy`.                                                                                                                                                                                                                                                                                                                                                                                        |
    | `reduce_all_density`      | `Union[float, bool]` | Percentage of rows to randomly remove from the input DataFrame. If True, 50% of the rows will be randomly removed. If False, no rows will be removed. Defaults to `50000`.                                                                                                                                                                                                                                                                                      |
    | `reduce_zero_density`     | `Union[float, bool]` | Percentage of rows with 0 value in the error column to randomly remove. If False, no rows with 0 value will be removed. Defaults to `False`.                                                                                                                                                                                                                                                                                                                    |
    | `reduce_non_zero_density` | `Union[float, bool]` | Percentage of rows with non-zero value in the error column to randomly remove. If False, no rows with non-zero value will be removed. Defaults to `False`.                                                                                                                                                                                                                                                                                                      |
    | `show_fig`                | `bool`               | If True, displays the plot.                                                                                                                                                                                                                                                                                                                                                                                                                     |

    ## Returns:
    None

    ## Raises:
    | Raise Name   | Description                                       |
    |:-------------|:--------------------------------------------------|
    | `ValueError` | If the input value for `error_type` is not valid. |

    ## Examples:
    >>> input_negDy_output_posDx_NUMERIC_ERRORS_DataFrame = pd.read_pickle('input_negDy_output_posDx_NUMERIC_ERRORS_DataFrame.pickle')
    >>> input_posDx_output_negDy_NUMERIC_ERRORS_DataFrame = pd.read_pickle('input_posDx_output_negDy_NUMERIC_ERRORS_DataFrame.pickle')
    >>> visualize_numeric_errors(input_negDy_output_posDx_NUMERIC_ERRORS_DataFrame, 
                                title = "Max Error", 
                                error_type = "maximum", 
                                input_name = "negDy", 
                                output_name = "posDx",
                                reduce_all_density = False,
                                reduce_zero_density = 50000,
                                reduce_non_zero_density = 50000)
    ...
    >>> visualize_numeric_errors(input_negDy_output_posDx_NUMERIC_ERRORS_DataFrame, 
                                title = "Error at middle y", 
                                error_type = "maximum_input_at_middle_y", 
                                input_name = "negDy", 
                                output_name = "posDx",
                                reduce_all_density = 100000,
                                reduce_zero_density = False,
                                reduce_non_zero_density = False)                       
    ...
    >>> visualize_numeric_errors(input_negDy_output_posDx_NUMERIC_ERRORS_DataFrame, 
                                title = "Zero Error", 
                                error_type = "Zero Error (Perfect Precision)", 
                                input_name = "negDy", 
                                output_name = "posDx",
                                reduce_all_density = False,
                                reduce_zero_density = 50000,
                                reduce_non_zero_density = 50000)
    ...

    ## Notes:
    - The input dataframe should contain columns for the input_name, output_name, and the errors.
    - The input_name column should contain integer values.
    - The output_name column should contain integer values.
    - The column names for input_name, output_name, and errors must match the names used in the function arguments.
    - The resulting plot will show the B scaled up, S scaled up, and y intercept values on the x, y, and z axes, respectively.
    - The color of each data point will be determined by the log10 of the appropriate column.

    ## Uses the following functions:

    | Function                                         | Return Type   | Description                                                                                                                                                                                        |
    |:-------------------------------------------------|:--------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `scale_dataframe`                                | `function`    | Scales up the `B precise (Decimal)` and `S precise (Decimal)` columns in a Pandas DataFrame by 2 raised to the appropriate scaling factor. Renames the columns to `B scaled up` and `S scaled up`. |
    | `reduce_density`                                 | `function`    | Randomly removes a specified percentage of the rows where values of 0 or non-zero values appear in the error in output column of a Pandas DataFrame.                                               |
    | `filter_dataframe_by_maximum_error`              | `function`    | Filters a DataFrame by the maximum error in the specified output column.                                                                                                                           |
    | `filter_dataframe_by_zero_error`                 | `function`    | Filters a DataFrame by the 0 error in the specified input column.                                                                                                                                  |
    | `filter_dataframe_by_maximum_input_for_middle_y` | `function`    | Filters a DataFrame by the maximum input value for a specific y intercept value.                                                                                                                   |
    | `get_color_dimension`                            | `function`    | Computes the color dimension for a data point, based on the error type.                                                                                                                            |                                                                                                                     |
    """
    global PRISM_LIBRARY
    func_dict = {'maximum' : (filter_dataframe_by_maximum_error,
                              [f'error in output {output_name} (Decimal)'],
                              'error in output (log10)'),
                'zero'     : (filter_dataframe_by_zero_error,
                              [f'input {input_name} (int)'],
                              f'input {input_name} (int) (log10)'),
                'maximum_input_at_middle_y' : (filter_dataframe_by_maximum_input_for_middle_y,
                              [f'error in output {output_name} (Decimal)'],
                              'error in output (log10)')
                }

    if error_type not in func_dict:
        raise ValueError('Invalid value for error_type. Must be "maximum", "zero", or "maximum_input_at_middle_y.')

    df = scale_dataframe(
            reduce_density(
                func_dict[error_type][0](
                        dataframe_to_visualize, 
                        input_name = input_name, 
                        output_name = output_name
                ),
                output_name = output_name,
                reduce_all_density = reduce_all_density,
                reduce_zero_density = reduce_zero_density, 
                reduce_non_zero_density = reduce_non_zero_density
            )
        )
    color_dimension = [get_color_dimension(x, error_type) for x in df[func_dict[error_type][1][0]]]
    color_label_text = func_dict[error_type][2]
    
    B_scaled_up_log10 = [float(Decimal(x).log10()) if x > 0 else float(-10) for x in df['B scaled up']]
    S_scaled_up_log10 = [float(Decimal(x).log10()) if x > 0 else float(-40) for x in df['S scaled up']]
    y_intercept_log10 = [float(Decimal(x).log10()) for x in df['y intercept (int)']]

    fig = px.scatter_3d(
        df, x = B_scaled_up_log10, y = S_scaled_up_log10, z = y_intercept_log10,
        color = color_dimension, 
        hover_data = df.columns,
        title = title,
        labels = {
            'B_scaled_up_log10': 'B scaled up (log10)',
            'S_scaled_up_log10': 'S scaled up (log10)',
            'y_intercept_log10': 'y intercept (int) (log10)',
        },
        color_continuous_scale = 'Viridis', # 'Viridis', 'Cividis', 'Inferno', 'Plasma', 'Magma', 'Turbo', 'Electric', 'Portland', 'Jet'
        template = 'plotly_dark'
    )

    fig.update_traces(marker = dict(
                                line = dict(width = 0,
                                            color = None),
                                size = 1),
                      selector = dict(mode = 'markers'))

    fig.update_layout(
        scene = {
            'xaxis': {'title': {'text': 'B scaled up (log10)'}},
            'yaxis': {'title': {'text': 'S scaled up (log10)'}},
            'zaxis': {'title': {'text': 'y intercept (int) (log10)'}},
            'camera': {'eye': {'x': -1.7, 'y': -1.7, 'z': 0.5}}
        },
        margin = {'l': 50, 'r': 50, 'b': 100, 't': 100},
        width = 1400, 
        height = 800,
        coloraxis_colorbar = dict(
            title = color_label_text,
            tickmode = 'auto',
            nticks = 5,
            )
        )
    
    fig.write_html(f'{filename}_error_type_{error_type}_input_{input_name}_output_{output_name}_PLOTLY_3D_SCATTER.html')
    
    if reference_prisms:
        for prism_pair in PRISM_LIBRARY:
            assert len(prism_pair[0]['vertices']) == len(prism_pair[1]['vertices']) == 8, "The list of prism coordinates should have 8 elements. Remake the library."
            for prism in prism_pair:
                            
                x_vertices = [coordinates[0] for coordinates in prism['vertices']]
                y_vertices = [coordinates[1] for coordinates in prism['vertices']]
                z_vertices = [coordinates[2] for coordinates in prism['vertices']]
                
                fig.add_trace(go.Mesh3d(
                    x = x_vertices,
                    y = y_vertices,
                    z = z_vertices,
                    i = [1, 1, 1, 1, 2, 2, 1, 0, 0, 3, 5, 4],
                    j = [3, 3, 6, 6, 6, 3, 0, 5, 3, 4, 6, 6],
                    k = [2, 0, 2, 5, 7, 7, 5, 4, 4, 7, 4, 7],
                    opacity = 0.6,
                    color = prism['color'],
                    flatshading = True,
                    hoverinfo = 'text',
                    hovertext = prism['annotation']
                ))
    
    fig.write_html(f'{filename}_error_type_{error_type}_input_{input_name}_output_{output_name}_PLOTLY_3D_SCATTER_W_PRISMS.html')
    
    if show_fig:
        fig.show()
    return(None)


# %%
def visualize_non_numeric_errors(
    dataframe_to_visualize: pd.DataFrame,
    filename: str = 'test_error_profiling',
    title: str = None,
    error_type: str = 'infinity',
    input_name: str = 'posDx',
    output_name: str = 'negDy',
    reduce_all_density: Union[int, bool] = 50000,
    reduce_zero_density: Union[int, bool] = False,
    reduce_non_zero_density: Union[int, bool] = False,
    show_fig: bool = False,
    reference_prisms: bool = True
    ) -> None:
    """
    ### visualize_non_numeric_errors creates a 3D scatter plot using Plotly Express to visualize the errors in a non-numeric dataset.

    ## Parameters:
    | Parameter names           | Parameter Types      | Parameter Descriptions                                                                                                                                                                                                                                                         |
    |:--------------------------|:---------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `dataframe_to_visualize`  | `pd.DataFrame`       | The input DataFrame to be visualized.                                                                                                                                                                                                                                          |
    | `filename`                | `str`                | The filename corresponding to the analysis being performed.                                                                                                                                                                                                                    |
    | `title`                   | `str`                | The title of the plot. If None, the title will not be displayed. Defaults to None.                                                                                                                                                                                             |
    | `error_type`              | `str`                | The type of error to visualize. Must be 'infinity' or 'solidity'. If 'infinity', the errors will be visualized as infinite errors, where the precise output is zero. If 'solidity', the errors will be visualized as solidity overflows or underflows. Defaults to 'infinity'. |
    | `input_name`              | `str`                | The name of the input column to use for filtering. Defaults to posDx.                                                                                                                                                                                                          |
    | `output_name`             | `str`                | The name of the output column to use for filtering. Defaults to negDy.                                                                                                                                                                                                         |
    | `reduce_all_density`      | `Union[float, bool]` | Percentage of rows to randomly remove from the input DataFrame. If True, 50% of the rows will be randomly removed. If False, no rows will be removed. Defaults to 50000.                                                                                                       |
    | `reduce_zero_density`     | `Union[float, bool]` | Percentage of rows with 0 value in the error column to randomly remove. If False, no rows with 0 value will be removed. Defaults to False.                                                                                                                                     |
    | `reduce_non_zero_density` | `Union[float, bool]` | Percentage of rows with non-zero value in the error column to randomly remove. If False, no rows with non-zero value will be removed. Defaults to False.                                                                                                                       |
    | `show_fig`                | `bool`               | If True, displays the plot.                                                                                                                                                                                                                                                 |

    ## Returns:
    None

    ## Examples:
    >>> input_negDy_output_posDx_INFINITY_ERRORS_DataFrame = pd.read_pickle('input_negDy_output_posDx_INFINITY_ERRORS_DataFrame.pickle')
    >>> visualize_non_numeric_errors(input_negDy_output_posDx_NUMERIC_ERRORS_DataFrame, 
                                     title = 'Input negDy -> posDx: Infinite Error (Precise Output == 0)', 
                                     error_type = 'infinity, 
                                     input_name = 'negDy', 
                                     output_name = 'posDx,
                                     reduce_all_density = 100000,
                                     reduce_zero_density = False,
                                     reduce_non_zero_density = False)
    ...     
    >>> input_negDy_output_posDx_SOLIDITY_ERRORS_DataFrame = pd.read_pickle('input_negDy_output_posDx_SOLIDITY_ERRORS_DataFrame.pickle')
    >>> visualize_non_numeric_errors(input_negDy_output_posDx_SOLIDITY_ERRORS_DataFrame, 
                                     title = 'Input negDy -> posDx: Solidity Overflow/Underflow and Zero Division Errors', 
                                     error_type = 'solidity, 
                                     input_name = 'negDy', 
                                     output_name = 'posDx,
                                     reduce_all_density = 100000,
                                     reduce_zero_density = False,
                                     reduce_non_zero_density = False)
    ...  
    
    ## Notes:
    - The input dataframe should contain columns for the input_name, output_name, and the errors.
    - The input_name column should contain categorical values.
    - The output_name column should contain integer values.
    - The column names for input_name, output_name, and errors must match the names used in the function arguments.
    - The resulting plot will show the B scaled up, S scaled up, and y intercept values on the x, y, and z axes, respectively.
    - The color of each data point will be determined by the error type specified in the function arguments.

    ## Uses the following functions:

    | Function          | Type       | Description                                                                                                                                                                                        |
    |:------------------|:-----------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `scale_dataframe` | `function` | Scales up the 'B precise (Decimal)' and 'S precise (Decimal)' columns in a Pandas DataFrame by 2 raised to the appropriate scaling factor. Renames the columns to 'B scaled up' and 'S scaled up'. |
    | `reduce_density`  | `function` | Randomly removes a specified percentage of the rows where values of 0 or non-zero values appear in the error in output column of a Pandas DataFrame.                                               |                                            |

    """
    global PRISM_LIBRARY
    
    df = scale_dataframe(
                         reduce_density(dataframe_to_visualize,
                                        output_name = output_name,
                                        reduce_all_density = reduce_all_density,
                                        reduce_zero_density = reduce_zero_density, 
                                        reduce_non_zero_density = reduce_non_zero_density))
    
    B_scaled_up_log10 = [float(Decimal(x).log10()) if x > 0 else float(-10) for x in df['B scaled up']]
    S_scaled_up_log10 = [float(Decimal(x).log10()) if x > 0 else float(-40) for x in df['S scaled up']]
    y_intercept_log10 = [float(Decimal(x).log10()) for x in df['y intercept (int)']]
    color_dimension = df[f'output {output_name} (int)']

    fig = px.scatter_3d(
        df, x = B_scaled_up_log10, y = S_scaled_up_log10, z = y_intercept_log10,
        color = color_dimension, 
        hover_data = df.columns,
        title = title,
        labels = {
            'B_scaled_up_log10': 'B scaled up (log10)',
            'S_scaled_up_log10': 'S scaled up (log10)',
            'y_intercept_log10': 'y intercept (int) (log10)',
        },
        color_continuous_scale = 'Portland', # 'Viridis', 'Cividis', 'Inferno', 'Plasma', 'Magma', 'Turbo', 'Electric', 'Portland', 'Jet'
        template = 'plotly_dark'
    )

    fig.update_traces(marker = dict(
                                line = dict(width = 0,
                                            color = None),
                                size = 1),
                      selector = dict(mode = 'markers'))

    fig.update_layout(
        scene = {
            'xaxis': {'title': {'text': 'B scaled up (log10)'}},
            'yaxis': {'title': {'text': 'S scaled up (log10)'}},
            'zaxis': {'title': {'text': 'y intercept (int) (log10)'}},
            'camera': {'eye': {'x': -1.7, 'y': -1.7, 'z': 0.5}}
        },
        margin = {'l': 50, 'r': 50, 'b': 100, 't': 100},
        width = 1400, 
        height = 800
    )
    
    fig.write_html(f'{filename}_error_type_{error_type}_input_{input_name}_output_{output_name}_PLOTLY_3D_SCATTER.html')
    
    if reference_prisms:
        for prism_pair in PRISM_LIBRARY:
            assert len(prism_pair[0]['vertices']) == len(prism_pair[1]['vertices']) == 8, "The list of prism coordinates should have 8 elements. Remake the library."
            for prism in prism_pair:
                            
                x_vertices = [coordinates[0] for coordinates in prism['vertices']]
                y_vertices = [coordinates[1] for coordinates in prism['vertices']]
                z_vertices = [coordinates[2] for coordinates in prism['vertices']]
                
                fig.add_trace(go.Mesh3d(
                    x = x_vertices,
                    y = y_vertices,
                    z = z_vertices,
                    i = [1, 1, 1, 1, 2, 2, 1, 0, 0, 3, 5, 4],
                    j = [3, 3, 6, 6, 6, 3, 0, 5, 3, 4, 6, 6],
                    k = [2, 0, 2, 5, 7, 7, 5, 4, 4, 7, 4, 7],
                    opacity = 0.6,
                    color = prism['color'],
                    flatshading = True,
                    hoverinfo = 'text',
                    hovertext = prism['annotation']
                ))
    
    fig.write_html(f'{filename}_error_type_{error_type}_input_{input_name}_output_{output_name}_PLOTLY_3D_SCATTER_W_PRISMS.html')
    
    if show_fig:
        fig.show()
    return(None)


# %%
def plot_numeric_errors_and_save_to_html(
    filename: str = 'test_error_profiling_1',
    number_of_data_points: int = 100000
    ) -> None:
    """
    ### plot_numeric_errors_and_save_to_html plots and saves visualizations of the numeric errors in pickled pandas DataFrames, and saves them to an HTML file.

    ## Parameters:
    | Parameter names         | Parameter Types   | Parameter Descriptions                                                                  |
    |:------------------------|:------------------|:----------------------------------------------------------------------------------------|
    | `filename`              | `str`             | A tag, appended as a prefix to the dataframes during their generation.                  |
    | `number_of_data_points` | `int`             | The maximum number of data points to include in the visualizations. Defaults to 100000. |

    ## Returns:
    None
    """
    inputs_and_outputs = ['posDx', 'negDy']
    error_types = ['zero', 'maximum', 'maximum_input_at_middle_y']
    title_descriptions = ['Zero Error (Perfect Precision)', 'Maximum Error', 'Error at middle y']
    combinations = [f'{filename}_input_{input}_output_{output}_NUMERIC_ERRORS_DataFrame.pickle' for input in inputs_and_outputs for output in inputs_and_outputs if input != output]
    for combination in combinations:
        input_output_str = combination.split('_input_')[1].split('_NUMERIC')[0]
        input_name, output_name = input_output_str.split('_output_')
        dataframe = pd.read_pickle(combination)
        for i, error_type in enumerate(error_types):
            visualize_numeric_errors(dataframe, 
                                     filename = filename, 
                                     title = f'Input {input_name} -> Output {output_name}: {title_descriptions[i]}',
                                     error_type = error_type, 
                                     input_name = input_name, 
                                     output_name = output_name,
                                     reduce_all_density = (number_of_data_points if error_type == 'zero' else False),
                                     reduce_zero_density = (False if error_type == 'zero' else number_of_data_points//2), 
                                     reduce_non_zero_density = (False if error_type == 'zero' else number_of_data_points//2), 
                                     show_fig = False,
                                     reference_prisms = True)
    return(None)


# %%
def plot_non_numeric_errors_and_save_to_html(
    filename: str = 'test_error_profiling_1',
    number_of_data_points: int = 100000
    ) -> None:
    """
    ### Plots and saves visualizations of the non-numeric errors in pickled pandas DataFrames, and saves them to an HTML file. 

    ## Parameters:
    | Parameter names         | Type   | Parameter Descriptions                                                                  |
    |:------------------------|:-------|:----------------------------------------------------------------------------------------|
    | `filename`              | `str`  | A tag, appended as a prefix to the dataframes during their generation.                  |
    | `number_of_data_points` | `int`  | The maximum number of data points to include in the visualizations. Defaults to 100000. |

    ## Returns:
    None
    """
    inputs_and_outputs = ['posDx', 'negDy']
    error_types = ['infinity', 'solidity']
    title_descriptions = {
        'infinity' : 'Infinite Error (Precise Output == 0)',
        'solidity' : 'Solidity Overflow/Underflow and Zero Division Errors'
        }
    combinations = [f'{filename}_input_{input}_output_{output}_{error_type.upper()}_ERRORS_DataFrame.pickle' for input in inputs_and_outputs for output in inputs_and_outputs for error_type in error_types if input != output]
    for combination in combinations:
        input_output_match = re.search(r'_input_(posDx|negDy)_output_(posDx|negDy)_', combination)
        input_name = input_output_match.group(1)
        output_name = input_output_match.group(2)
        error_type_match = re.search(r'(INFINITY_ERRORS|SOLIDITY_ERRORS)', combination)
        error_type = error_type_match.group(1).lower().split("_")[0]
        dataframe = pd.read_pickle(combination)
        if len(dataframe) == 0:
            print(f'{combination} is an empty dataframe. Moving on...')
        else:
            visualize_non_numeric_errors(dataframe, 
                                        filename = filename, 
                                        title = f'Input {input_name} -> Output {output_name}: {title_descriptions[error_type]}',
                                        error_type = error_type,
                                        input_name = input_name, 
                                        output_name = output_name,
                                        reduce_all_density = number_of_data_points, 
                                        reduce_zero_density = False, 
                                        reduce_non_zero_density = False, 
                                        show_fig = False,
                                        reference_prisms = True)
    return(None)


# %% [markdown]
# # Compare two outputs

# %%
def check_inputs_are_identical(
    main_dataframe_1: pd.DataFrame,
    main_dataframe_2: pd.DataFrame,
    expected_identical_columns: List[str]
    ) -> bool:
    """
    ### Compares two input dataframes to determine if the specified columns have identical values.

    ## Parameters:
    | Parameter Name               | Type           | Description                                                                                 |
    |:-----------------------------|:---------------|:--------------------------------------------------------------------------------------------|
    | `main_dataframe_1`           | `pd.DataFrame` | The first input dataframe to compare.                                                       |
    | `main_dataframe_2`           | `pd.DataFrame` | The second input dataframe to compare.                                                      |
    | `expected_identical_columns` | `List`         | A list of the column names where the rows in both data frames are expected to be identical. |

    ## Returns:
    | Returns            | Type   | Description                                                                                     |
    |:-------------------|:-------|:------------------------------------------------------------------------------------------------|
    | `identical_inputs` | `bool` | A boolean indicating whether the specified columns in the two dataframes have identical values. |

    ## Example:
    >>> df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 7], 'C': [7, 8, 9]})
    >>> df2 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})
    >>> check_inputs_are_identical(df1, df2, ['C'])
    True
    >>> check_inputs_are_identical(df1, df2, ['B'])
    Dataframes differ unexpectedly on 2:
    main_dataframe_1[2] = {'B': 7}
    main_dataframe_2[2] = {'B': 6}
    """
    main_dataframe_1 = main_dataframe_1.filter(expected_identical_columns)
    main_dataframe_2 = main_dataframe_2.filter(expected_identical_columns)
    identical_inputs = main_dataframe_1.equals(main_dataframe_2)
    if not identical_inputs:
        unequal_rows = ~(main_dataframe_1 == main_dataframe_2)
        first_unequal_row = unequal_rows.any(axis=1).idxmax()
        unequal_cols = unequal_rows.loc[first_unequal_row]
        unequal_cols = unequal_cols[unequal_cols].index.tolist()
        print(f"Dataframes differ unexpectedly on {first_unequal_row}:")
        print(f"  main_dataframe_1[{first_unequal_row}] = {main_dataframe_1.loc[first_unequal_row, unequal_cols].to_dict()}")
        print(f"  main_dataframe_2[{first_unequal_row}] = {main_dataframe_2.loc[first_unequal_row, unequal_cols].to_dict()}")
    return(identical_inputs)


# %%
def rename_output_columns_in_main_dataframe(
    main_dataframe: pd.DataFrame,
    expected_output_columns: List[str],
    dataframe_output_suffix: str
    ) -> pd.DataFrame:
    """
    ### Renames specified columns in a given pandas DataFrame by adding a given suffix to their names.

    ## Parameters:
    | Parameter Name            | Type           | Description                               |
    |:--------------------------|:---------------|:------------------------------------------|
    | `main_dataframe`          | `pd.DataFrame` | The input dataframe to rename columns in. |
    | `expected_output_columns` | `List[str]`    | A list of the column names to rename.     |
    | `dataframe_output_suffix` | `str`          | The suffix to add to the column names.    |

    ## Returns:
    | Return Name              | Type           | Description                                     |
    |:-------------------------|:---------------|:------------------------------------------------|
    | `renamed_main_dataframe` | `pd.DataFrame` | A dataframe with the specified columns renamed. |
    """
    renamed_main_dataframe = main_dataframe.rename(columns={col: col + dataframe_output_suffix for col in expected_output_columns})
    return(renamed_main_dataframe)


# %%
def slice_output_columns_from_main_dataframe(
    main_dataframe: pd.DataFrame,
    expected_output_columns: List[str],
    dataframe_output_suffix: str
    ) -> pd.DataFrame:
    """
    ### Slices the specified columns from the main dataframe and adds a suffix to the column names.

    ## Parameters:
    | Parameter Name            | Type           | Description                                                 |
    |:--------------------------|:---------------|:------------------------------------------------------------|
    | `main_dataframe`          | `pd.DataFrame` | The dataframe from which to slice the specified columns.    |
    | `expected_output_columns` | `List[str]`    | A list of the column names to be sliced from the dataframe. |
    | `dataframe_output_suffix` | `str`          | The suffix to add to the column names.                      |

    ## Returns:
    | Return name           | Type           | Description                                                                               |
    |:----------------------|:---------------|:------------------------------------------------------------------------------------------|
    | `output_columns_only` | `pd.DataFrame` | A dataframe containing only the sliced columns with the added suffix in the column names. |
    """
    output_columns_only = main_dataframe[expected_output_columns].add_suffix(dataframe_output_suffix)
    return(output_columns_only)


# %%
def merge_renamed_dataframes(
    renamed_dataframe_1: pd.DataFrame,
    renamed_dataframe_2: pd.DataFrame,
    ) -> pd.DataFrame:
    """
    ### Merges two dataframes with renamed columns by concatenating them horizontally.

    ## Parameters:
    | Parameter Name        | Type           | Description                                |
    |:----------------------|:---------------|:-------------------------------------------|
    | `renamed_dataframe_1` | `pd.DataFrame` | The first dataframe with renamed columns.  |
    | `renamed_dataframe_2` | `pd.DataFrame` | The second dataframe with renamed columns. |

    ## Returns:
    | Return name        | Type           | Description                                                   |
    |:-------------------|:---------------|:--------------------------------------------------------------|
    | `merged_dataframe` | `pd.DataFrame` | The merged dataframe with columns from both input dataframes. |
    """
    merged_dataframe = pd.concat([renamed_dataframe_1, renamed_dataframe_2], axis = 1)
    return merged_dataframe


# %%
def merge_dataframes_to_compare_and_save(
    first_dataframe: pd.DataFrame,
    second_dataframe: pd.DataFrame,
    suffix_list: List[str] = [' (max = 256)', ' (max = 512)'],
    comparison_filename: str = 'comparison_filename'
    ) -> pd.DataFrame:
    """
    ### Merges two dataframes and saves the result.

    ## Parameters:
    | Parameter Name        | Type           | Description                                                                                          |
    |:----------------------|:---------------|:-----------------------------------------------------------------------------------------------------|
    | `first_dataframe`     | `pd.DataFrame` | The first input dataframe to merge.                                                                  |
    | `second_dataframe`    | `pd.DataFrame` | The second input dataframe to merge.                                                                 |
    | `suffix_list`         | `List[str]`    | A list of suffixes to apply to the error column names. Defaults to [' (max = 256)', ' (max = 512)']. |
    | `comparison_filename` | `str`          | The filename for the resulting comparison dataframe. Defaults to 'comparison_filename'.              |
  
    ## Returns:
    | Return Name        | Type           | Description                                       |
    |:-------------------|:---------------|:--------------------------------------------------|
    | `merged_dataframe` | `pd.DataFrame` | The merged dataframe of the two input dataframes. |

    ## Raises:
    | Raises           | Description                                                                        |
    |:-----------------|:-----------------------------------------------------------------------------------|
    | `AssertionError` | If the specified input columns in the two dataframes do not have identical values. |

    ## Notes:
    - first_dataframe and second_dataframe must contain the following columns:

    | Column Name                              | Series Description                                                                                                                          | Series Type   |
    |:-----------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------|:--------------|
    | precise input P_a (Decimal)              | The user input and curve parameter, `P_a`, with arbitrary floating-point precision.                                                         | `float`       |
    | precise input P_b (Decimal)              | The user input and curve parameter, `P_a`, with arbitrary floating-point precision.                                                         | `float`       |
    | y (int)                                  | The user input and token balance of the curve, `y`, as an integer.                                                                          | `int`         |
    | y intercept (int)                        | The user input and token balance of the curve,, `y_int`, as an integer.                                                                     | `int`         |
    | input posDx (int)                        | The user input and trade quantity requested to deliver to the protocol, `posDx`, as an integer.                                             | `int`         |
    | input negDy (int)                        | The user input and trade quantity requested to sequester from the protocol, `negDy`, as an integer.                                         | `int`         |
    | B precise (Decimal)                      | The `B` value, calculated with arbitrary floating-point precision from the user input `P_b`.                                                | `float`       |
    | B reconstituted (int)                    | The `B` integer value after reconstitution from storage (i.e. some precision loss due to compression/decompression)                         | `int`         |
    | error in B reconstitution (Decimal)      | The specific relative error in the `B` value attributed to compression/decompression only.                                                  | `float`       |
    | error in B compared to precise (Decimal) | The general relative error in the `B` value, calculated from its reconstituted value versus its precise value.                              | `float`       |
    | S precise (Decimal)                      | The `S` value, calculated with high precision from the user inputs `P_a` and `P_b`.                                                         | `float`       |
    | S reconstituted (int)                    | The `S` value after reconstitution from storage (i.e. some precision loss due to compression/decompression).                                | `int`         |
    | error in S reconstitution (Decimal)      | The specific relative error in the `S` value attributed to compression/decompression only.                                                  | `float`       |
    | error in S compared to precise (Decimal) | The general relative error in the `S` value, calculated from its reconstituted value versus its precise value.                              | `float`       |
    | precise output negDy (int)               | The integer result of `negDy`, calculated with arbitrary floating-point precision from the user input `posDx`.                              | `float`       |
    | output negDy (int)                       | The fixed-point output `negDy`, calculated from the user input `posDx` and while emulating the constraints of the Ethereum Virtual Machine. | `int`         |
    | precise output posDx (int)               | The integer result of `posDx`, calculated with arbitrary floating-point precision from the user input `negDy`.                              | `int`         |
    | output posDx (int)                       | The fixed-point output `posDx`, calculated from the user input `negDy` and while emulating the constraints of the Ethereum Virtual Machine. | `int`         |
    | error in output negDy (Decimal)          | The specific relative error between the fixed-point, and high-precision `negDy` outputs calculated from identical, integer `posDx` inputs.  | `float`       |
    | error in output posDx (Decimal)          | The specific relative error between the fixed-point, and high-precision `posDx` outputs calculated from identical, integer `negDy` inputs.  | `float`       |
    | id (int)                                 | The 'original' index number, which is maintained in all future slicing and other manipulations of this dataframe.                           | `int`         |

    - Performs the following actions:
    - Compares the two dataframes to ensure that the inputs columns have identical values.
    - Renames the columns in the first dataframe with the output suffix.
    - Slices the output columns in the second dataframe, and renames those columns with the output suffix.
    - Merges the two renamed dataframes into a single dataframe.
    - Adds a unique ID column if it does not exist.
    - Saves the merged dataframe as a pickle file.
    """
    expected_identical_columns = ['precise input P_a (Decimal)', 
                                  'precise input P_b (Decimal)', 
                                  'y (int)',
                                  'y intercept (int)', 
                                  'input posDx (int)', 
                                  'input negDy (int)',
                                  'B precise (Decimal)', 
                                  'B reconstituted (int)',
                                  'error in B reconstitution (Decimal)',
                                  'error in B compared to precise (Decimal)', 
                                  'S precise (Decimal)',
                                  'S reconstituted (int)', 
                                  'error in S reconstitution (Decimal)',
                                  'error in S compared to precise (Decimal)',
                                  'precise output negDy (int)',
                                  'precise output posDx (int)']
    
    expected_output_columns = ['output negDy (int)', 
                               'output posDx (int)',
                               'error in output negDy (Decimal)', 
                               'error in output posDx (Decimal)']
    
    assert check_inputs_are_identical(first_dataframe, second_dataframe, expected_identical_columns), "Input columns are not identical"
    renamed_main_dataframe_1 = rename_output_columns_in_main_dataframe(first_dataframe, expected_output_columns, suffix_list[0])
    renamed_output_columns_from_main_dataframe_2 = slice_output_columns_from_main_dataframe(second_dataframe, expected_output_columns, suffix_list[1])
    merged_dataframe = merge_renamed_dataframes(renamed_main_dataframe_1, renamed_output_columns_from_main_dataframe_2)
    if 'id (int)' not in merged_dataframe.columns:
        merged_dataframe['id (int)'] = list(merged_dataframe.index)
    merged_dataframe.to_pickle(f'{comparison_filename}_FULL_DATAFRAME.pickle')
    return(merged_dataframe)


# %%
def separate_identical_errors(
    dataframe: pd.DataFrame, 
    output_type: str, 
    suffix_list: List[str] = [' (max = 256)', ' (max = 512)']
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    ### Separates the rows of a given dataframe into two dataframes based on whether the values in specified error columns are identical.

    ## Parameters:
    | Parameter Name   | Type           | Description                                                                                          |
    |:-----------------|:---------------|:-----------------------------------------------------------------------------------------------------|
    | `dataframe`      | `pd.DataFrame` | The DataFrame to separate.                                                                           |
    | `output_type`    | `str`          | The output type to apply the separation to, either 'negDy' or 'posDx'.                               |
    | `suffix_list`    | `List[str]`    | A list of suffixes to apply to the error column names. Defaults to [' (max = 256)', ' (max = 512)']. |

    ## Returns:
    | Return name        | Type                                | Description                                                                                                                               |
    |:-------------------|:------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------|
    | `identical_errors` | `pd.DataFrame`                      | A pandas dataframe containing exclusively the input/output pairs that are unaffected between the implementations being compared.          |
    | `changed_errors`   | `pd.DataFrame`                      | A pandas dataframe containing exclusively the input/output pairs that were changed as a result of the implementations being compared.     |
    |                    | `Tuple[pd.DataFrame, pd.DataFrame]` | A tuple of `identical_errors` and `changed_errors`, in that order.                                                                        |
    """
    identical_errors = dataframe[
        pd.to_numeric(
            dataframe[f'error in output {output_type} (Decimal){suffix_list[0]}'], 
            errors='coerce'
        ) == pd.to_numeric(
            dataframe[f'error in output {output_type} (Decimal){suffix_list[1]}'], 
            errors='coerce'
        )
    ].reset_index(drop=True)
    changed_errors = dataframe[
        pd.to_numeric(
            dataframe[f'error in output {output_type} (Decimal){suffix_list[0]}'], 
            errors='coerce'
        ) != pd.to_numeric(
            dataframe[f'error in output {output_type} (Decimal){suffix_list[1]}'], 
            errors='coerce'
        )
    ].reset_index(drop=True)
    return (identical_errors, changed_errors)


# %%
def separate_numeric_errors(
    dataframe: pd.DataFrame,
    output_type: str,
    suffix_list: List[str] = [' (max = 256)', ' (max = 512)']
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    ### Separates the rows of a given dataframe into two dataframes based on whether the values in specified error columns are numeric.

    ## Parameters:
    | Parameter Name   | Type           | Description                                                                                          |
    |:-----------------|:---------------|:-----------------------------------------------------------------------------------------------------|
    | `dataframe`      | `pd.DataFrame` | The DataFrame to separate.                                                                           |
    | `output_type`    | `str`          | The output type to apply the separation to, either 'negDy' or 'posDx'.                               |
    | `suffix_list`    | `List[str]`    | A list of suffixes to apply to the error column names. Defaults to [' (max = 256)', ' (max = 512)']. |

    ## Returns:
    | Parameter Name            | Type                                | Description                                                                                                     |
    |:--------------------------|:------------------------------------|:----------------------------------------------------------------------------------------------------------------|
    | `numeric_errors_only`     | `pd.DataFrame`                      | A pandas dataframe containing exclusively the input/output pairs that have numeric error values.                |
    | `non_numeric_errors_only` | `pd.DataFrame`                      | A pandas dataframe containing exclusively the input/output pairs that at least one non-numeric error value.     |
    |                           | `Tuple[pd.DataFrame, pd.DataFrame]` | A tuple of `numeric_errors_only` and `non_numeric_errors_only`, in that order.                                  |
    """
    numeric_errors_only = dataframe[
        pd.to_numeric(dataframe[f'error in output {output_type} (Decimal){suffix_list[0]}'], errors='coerce').notna() &
        pd.to_numeric(dataframe[f'error in output {output_type} (Decimal){suffix_list[1]}'], errors='coerce').notna()
    ].reset_index(drop=True)
    non_numeric_errors_only = dataframe[
        ~pd.to_numeric(dataframe[f'error in output {output_type} (Decimal){suffix_list[0]}'], errors='coerce').notna() |
        ~pd.to_numeric(dataframe[f'error in output {output_type} (Decimal){suffix_list[1]}'], errors='coerce').notna()
    ].reset_index(drop=True)
    return(numeric_errors_only, non_numeric_errors_only)


# %%
def process_comparison_data_frames(
    path_to_first_dataframe: str,
    path_to_second_dataframe: str,
    comparison_filename: str,
    suffix_list: List[str],
    ) -> None:
    """
    ### Loads two pandas dataframes from given paths, merge and process them, and save the processed dataframes to disk.

    ## Parameters:
    | Parameter Name             | Type        | Description                                                                        |
    |:---------------------------|:------------|:-----------------------------------------------------------------------------------|
    | `path_to_first_dataframe`  | `str`       | The file path to the first pandas dataframe.                                       |
    | `path_to_second_dataframe` | `str`       | The file path to the second pandas dataframe.                                      |
    | `comparison_filename`      | `str`       | A string representing the name of the comparison, used to save the processed data. |
    | `suffix_list`              | `List[str]` | A list of suffixes used to identify and group the columns of the dataframes.       |

    ## Returns:
        None

    ## Example:
    >>> path_to_first_dataframe = 'fixed_scaling_factor_48_FULL_DATAFRAME.pickle'
    >>> path_to_second_dataframe = 'fixed_scaling_factor_48_BIGNUMBER_FULL_DATAFRAME.pickle'
    >>> comparison_filename = 'SF48_256_vs_512'
    >>> first_dataframe_output_suffix = ' (max = 256)'
    >>> second_dataframe_output_suffix = ' (max = 512)'
    >>> suffix_list = [first_dataframe_output_suffix, second_dataframe_output_suffix]
    >>> process_comparison_data_frames(path_to_first_dataframe, path_to_second_dataframe, comparison_filename, suffix_list)

    ## Notes:
    - The function loads the pandas dataframes located at `path_to_first_dataframe` and `path_to_second_dataframe` using pandas' `read_pickle` method.
    - The two dataframes are then merged together using the `merge_dataframes_to_compare_and_save` function.
    - The merged dataframe is then processed using a set of functions to separate the data into various categories (identical errors, changed errors, numeric errors only, and non-numeric errors). 
    - Each processed dataframe is saved as a pickle file with a filename that includes the 'comparison_filename'+'descriptive_title_of_the_dataframe.pickle'. 
    - If the columns of the input dataframes cannot be identified using the provided suffixes, a `ValueError` is raised.
    """
    main_dataframe_1 = pd.read_pickle(path_to_first_dataframe)
    main_dataframe_2 = pd.read_pickle(path_to_second_dataframe)
    merged_dataframe = merge_dataframes_to_compare_and_save(main_dataframe_1, main_dataframe_2, suffix_list, comparison_filename)
    (input_posDx_output_negDy_DataFrame, 
    input_negDy_output_posDx_DataFrame) = split_main_dataframe_by_input_type(merged_dataframe, 
                                                                                    comparison = True, 
                                                                                    suffix_list = suffix_list)
    (input_posDx_output_negDy_IDENTICAL_ERRORS_DataFrame, 
    input_posDx_output_negDy_CHANGED_ERRORS_DataFrame) = separate_identical_errors(input_posDx_output_negDy_DataFrame, 'negDy', suffix_list)
    (input_negDy_output_posDx_IDENTICAL_ERRORS_DataFrame, 
    input_negDy_output_posDx_CHANGED_ERRORS_DataFrame) = separate_identical_errors(input_negDy_output_posDx_DataFrame, 'posDx', suffix_list)
    (input_posDx_output_negDy_NUMERIC_ERRORS_ONLY_DataFrame,
    input_posDx_output_negDy_NON_NUMERIC_ERRORS_DataFrame) = separate_numeric_errors(input_posDx_output_negDy_CHANGED_ERRORS_DataFrame, 'negDy', suffix_list)
    (input_negDy_output_posDx_NUMERIC_ERRORS_ONLY_DataFrame, 
    input_negDy_output_posDx_NON_NUMERIC_ERRORS_DataFrame) = separate_numeric_errors(input_negDy_output_posDx_CHANGED_ERRORS_DataFrame, 'posDx', suffix_list)
    processed_dataframes = [input_posDx_output_negDy_IDENTICAL_ERRORS_DataFrame,
                            input_negDy_output_posDx_IDENTICAL_ERRORS_DataFrame,
                            input_posDx_output_negDy_NUMERIC_ERRORS_ONLY_DataFrame,
                            input_posDx_output_negDy_NON_NUMERIC_ERRORS_DataFrame,
                            input_negDy_output_posDx_NUMERIC_ERRORS_ONLY_DataFrame,
                            input_negDy_output_posDx_NON_NUMERIC_ERRORS_DataFrame]
    filenames = [f'{comparison_filename}_input_posDx_output_negDy_IDENTICAL_ERRORS_DataFrame.pickle',
                 f'{comparison_filename}_input_negDy_output_posDx_IDENTICAL_ERRORS_DataFrame.pickle',
                 f'{comparison_filename}_input_posDx_output_negDy_NUMERIC_ERRORS_ONLY_DataFrame.pickle',
                 f'{comparison_filename}_input_posDx_output_negDy_NON_NUMERIC_ERRORS_DataFrame.pickle',
                 f'{comparison_filename}_input_negDy_output_posDx_NUMERIC_ERRORS_ONLY_DataFrame.pickle',
                 f'{comparison_filename}_input_negDy_output_posDx_NON_NUMERIC_ERRORS_DataFrame.pickle']
    for df, pickle_filename in zip(processed_dataframes, filenames):
        df.to_pickle(f'{pickle_filename}')
    return(None)


# %% [markdown]
# # Run the simulation and measure error profile

# %%
# approximately 48 minutes to run this cell

input_parameters = {
    'min_value' : int(0),
    'max_value' : int(2**256 - 1),
    'max_B_and_S_bits' : int(96),
    'mantissa_bits' : int(48),
    'exponent_bits' : int(6),
    'scaling_factor' : int(48),
    'P_b_start' : int(96), # 2**n
    'P_b_stop' : int(-96), # 2**n
    'P_b_number_of_points' : int(100),
    'S_start' : int(96), # 2**n
    'S_stop' : int(-96), # 2**n
    'S_number_of_points' : int(100),
    'y_int_start' : int(0), # 2**n
    'y_int_stop' : int(112), # 2**n
    'y_int_number_of_points' : int(100),
    'secondary_array_n' : int(2) # generates (2**n) + 1 logarithmically spaced integer values
}

filename = 'WHOLE_CODE_TEST_256'

main_data_frame = calculate_error_profile(input_parameters, filename)
process_main_data_frame(main_data_frame, filename)
plot_numeric_errors_and_save_to_html(filename, number_of_data_points = 200000)
plot_non_numeric_errors_and_save_to_html(filename, number_of_data_points = 200000)

# %%
# approximately 49 minutes to run this cell

input_parameters = {
    'min_value' : int(0),
    'max_value' : int(2**512 - 1),
    'max_B_and_S_bits' : int(96),
    'mantissa_bits' : int(48),
    'exponent_bits' : int(6),
    'scaling_factor' : int(48),
    'P_b_start' : int(96), # 2**n
    'P_b_stop' : int(-96), # 2**n
    'P_b_number_of_points' : int(100),
    'S_start' : int(96), # 2**n
    'S_stop' : int(-96), # 2**n
    'S_number_of_points' : int(100),
    'y_int_start' : int(0), # 2**n
    'y_int_stop' : int(112), # 2**n
    'y_int_number_of_points' : int(100),
    'secondary_array_n' : int(2) # generates (2**n) + 1 logarithmically spaced integer values
}

filename = 'WHOLE_CODE_TEST_512'

main_data_frame = calculate_error_profile(input_parameters, filename)
process_main_data_frame(main_data_frame, filename)
plot_numeric_errors_and_save_to_html(filename, number_of_data_points = 200000)
plot_non_numeric_errors_and_save_to_html(filename, number_of_data_points = 200000)

# %%
# approximately 21 minutes to run this cell (just plotting)

# filename = 'PLOT_TEST_ONLY'
# plot_numeric_errors_and_save_to_html(filename, number_of_data_points = 200000)
# plot_non_numeric_errors_and_save_to_html(filename, number_of_data_points = 200000)

# %%
# approximately 7 minutes to run this cell

path_to_first_dataframe = 'WHOLE_CODE_TEST_256_FULL_DATAFRAME.pickle'
path_to_second_dataframe = 'WHOLE_CODE_TEST_512_FULL_DATAFRAME.pickle'
comparison_filename = 'WHOLE_CODE_256_vs_512'
first_dataframe_output_suffix = ' (max = 256)'
second_dataframe_output_suffix = ' (max = 512)'
suffix_list = [first_dataframe_output_suffix, second_dataframe_output_suffix]

process_comparison_data_frames(path_to_first_dataframe, path_to_second_dataframe, comparison_filename, suffix_list)

# %%
# total run time approximately 2 hours 10 minutes

# %%
moai = """
                                                                                
                                                                                
                                                                                
                                                                                
                          ,(&@(,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,                  
                   ,%@@@@@@@@@@,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.                 
              @@@@@@@@@@@@@@@@@&,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.                
              @@@@@@@@@@@@@@@@@@/,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,                
              @@@@@@@@@@@@@@@@@@@,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,               
              @@@@@@@@@@@@@@@@@@@%,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,              
              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.              
              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.                
          (((((((((&@@@@@@@@@@@@@@@@@@@@@@@@@@@(,,,,,,,%@@@@@,                  
          (((((((((@@@@@@@@@@@@@@@@@@@@@@@@@@((((,,,,,,,#@@.                    
         ,((((((((#@@@@@@@@@@@/////////////((((((/,,,,,,,,                      
         *((((((((#@@@@@@@@@@@#,,,,,,,,,,,,/((((((/,,,,,,,,                     
         /((((((((#@@@@@@@@@@@@*,,,,,,,,,,,,(((((((*,,,,,,,,                    
         (((((((((%@@@@@@@@@@@@&,,,,,,,,,,,,/(((((((,,,,,,,,,.                  
        .(((((((((&@@@@@@@@@@@@@/,,,,,,,,,,,,((((((((,,,,,,,,,,                 
        *(((((((((@@@@@@@@@@@@@@@,,,,,,,,,,,,*((((((((,,,,,,,,,,                
        /((((((((#@@@@@@@@@@@@@@@@/,,,,,,,,,,,((((((((/,,,,,,,,,,.              
        (((((((((%@@@@@@@@@@@@@@@@@(,,,,,,,,,,*((((((((/,,,,,,,,,,,             
        (((((((((%@@@@@@@@@@@@@@@@@@%,,,,,,,,,,(((((((((*,,,,,,,,,,,            
       ,(((((((((&@@@@@@@@@@@@@@@@@@@&,,,,,,,,,*(((((((((*,,,,,,,,,,,.          
       ((((((((((@@@@@@@@@@@@@@@@@@@@@@*,,,,,,,,((((((((((,,,,,,,,,,,,,         
       ((((((((((@@@@@@@@@@@@@@@@@@@@@@@(,,,,,,,*((((((((((,,,,,,,,,,,,,        
       (((((((((#@@@@@@@@@@@@&#(((((((((/,,,,,,,,/((((((((((,,,,,,,,,,,,,       
       %@@@@@@@@@@@@@@@@@@((((((((((((((/,,,,,,,,*(((((((#&@@@@@@@@@@@@@.       
        &@@@@@@@@@@@@@@@@@@#((((((((((((*,,,,,,,,,/((((%@@@@@@@@@@@@@%          
         &@@@@@@@@@@@@@@@@@@%(((((((((((*,,,,,,,,,*(#@@@@@@@@@@@@@@*            
         /@@@@@@@@@@@@@@@@@@@%((((((((((*,,,,,,,,,,,,,,,,,,,,,,,,,              
         %@@@@@@@@@@@@@@@@@@@@&(((((((((*,,,,,,,,,,,,,,,,,,,,,,,,,,             
         @@@@@@@@@@@@@@@@@@@@@@@((((((((,,,,,,,,,,,,,,,,,,,,,,,,,,,,            
        ,@@@@@@@@@@@@@@@@@@@@@@@@#((((((,,,,,,,,,,,,,,,,,,,,,,,,,,,,,           
        #@@@@@@@@@@@@@@@@@@@@@@@@@#(((((,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.          
        &@@@@@@@@@@@@@@@@@@@@@@@@@@%((((,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,          
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@&(((,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,         
       (@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@((,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,        
       MB@RICHARDSON@BANCOR@(2023)@@@@@/,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,       
"""
