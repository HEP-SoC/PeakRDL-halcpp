---
sidebar_position: 2
---
# FieldNode

`FieldNode` is a template class that represents a `field` component in SystemRDL.<br/>
`FieldNode` is the lowest node in the hierarchy, and it can only be instantiated within a `RegNode` component.

## `FieldBase`

`FieldBase` is a base class providing `constexpr` constants for basic information about the field.
The base class does not provide any `write` or `read` capabilities.

It is a template that takes the following template arguments

```cpp
template <uint32_t START_BIT, uint32_t END_BIT, typename PARENT_TYPE>
class FieldBase;
```

`START_BIT` and `END_BIT` represent the position of the field within the containing register. They are integers and represent `LSB` and `MSB` respectively.

`PARENT_TYPE` accepts a specialization of a `RegNode` template, and is the type of the containing register.
It is necessary to pass this type, because the `write` and `read` methods of the field will pass these requests to the parent register, along with the value written.


## `FieldRdMixin` and `FieldWrMixin`

Since the `FieldBase` class does not provide any `write` or `read` capabilities, these two `Mixins` are supposed to provide the additional capabilities to the fields.
They are supposed to provide `setters` and `getters` for the fields, along with operator overloads.
The memory access is not done by these mixins, but the requests are instead passed to the register nodes.

### Field access methods

The 2 mixins will provide at least the `get()` and `set()` methods for accessing the field.
The execution of getters and setters will depend on the type of the containing register.

#### Writing to a field

In case of a writing a value to a field there are 2 cases.

##### 1. Containing register is `write only`

In this case the value passed to the register for writing will just be the value written to the field shifted by `LSB`.
This will correspond to only 1 write memory access, and an additional shifting operation if the passed value is a variable.

##### 2. Containing register is `rw`

In this case it is necessary to read first the register value and apply a mask corresponding to the location of the field.

The field `set()` method will first read a value from the containing register, apply a mask, and `|` (OR) the value with the shifted value of the passed argument to the `set()` method.

This will correspond to 1 read memory operation first, followed by arithmetic operations for masking (can vary) and a write memory operation.

#### Reading from a field

In case of reading from a field, the operation does not depend on the containing register, and the value returned from `get()` function will just be containing register value with applied mask and shifted right by `LSB`.
It will in this case have 1 read memory access, and arithmetic operation for mask and shifting (can vary).

## `FieldNode`

`FieldNode` is a template class inheriting the parameter pack of mixins. The prototype is as shown:
```cpp
template <typename... FieldMixins>
class FieldNode : public FieldMixins...
```

In order to provide Registers and Fields that have `Read`, `Write` or `ReadWrite` capabilities, the templates `FieldNode` are inheriting parameter pack of `Mixins` meant to provide the additional functionality.

For example:
*   `FieldNode` inheriting only `FieldRdMixin` will be a `read-only` field.
*   `FieldNode` inheriting only `FieldWrMixin` will be a `write-only` field.
*   `FieldNode` inheriting both `FieldWrMixin` and `FieldRdMixin` will be a `read-write` field.

In order to ease the use of these templates, common specializations of `FieldNode` is already provided under the names:

###  `FieldRO`
is a `read-only` field with a declaration:

```cpp
template <uint32_t START_BIT, uint32_t END_BIT, typename PARENT_TYPE>
using FieldRO = ...
```

###  `FieldWO`
is a `write-only` field with a declaration:

```cpp
template <uint32_t START_BIT, uint32_t END_BIT, typename PARENT_TYPE>
using FieldWO = ...
```

### `FieldRW`
is a `read-write` field with a declaration:

```cpp
template <uint32_t START_BIT, uint32_t END_BIT, typename PARENT_TYPE>
using FieldRW = ...
```


It is advised to use these specializations to construct your fields.
