---
sidebar_position: 5
---
# MemNode

A simple implementation of `MemNode` is provided that implements SystemRDL `mem` components.

## `MemNode`

`MemNode` is a template class that represents a `mem` component in SystemRDL.
It must be instantiated within an `AddrmapNode`.

```cpp
template <uint32_t BASE, uint32_t SIZE, typename PARENT_TYPE>
class MemNode;
```

The template parameters are:
*   `BASE` is the base address offset within the containing `AddrmapNode`.
*   `SIZE` is the size of the memory region in bytes.
*   `PARENT_TYPE` is the type of the containing `AddrmapNode`.

### Access methods

`MemNode` provides `get()` and `set()` methods for word-level access to the memory region.
All requests are forwarded to the parent node with the offset applied.

