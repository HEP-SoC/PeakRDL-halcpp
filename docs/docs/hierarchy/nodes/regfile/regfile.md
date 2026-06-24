---
sidebar_position: 7
---
# RegFileNode

`RegFileNode` is a template class that represents a `regfile` component in SystemRDL.<br/>
`RegFileNode` can contain only `RegNodes` or `RegFileNodes`, and it must be instantiated within `AddrmapNode` or `RegFileNode`.

## `RegFileBase`

`RegFileBase` is a class providing `constexpr` constants for basic information about the register file.

It is a template that takes the following template arguments

```cpp
template <uint32_t BASE, typename PARENT_TYPE>
class RegfileNode {
```

The template parameters are:
*   `BASE` is an address offset within an `AddrmapNode` or `RegFileNode`.
*   `PARENT_TYPE` accepts a specialization of an `AddrmapNode` or `RegFileNode` template, and is the type of the containing node.

