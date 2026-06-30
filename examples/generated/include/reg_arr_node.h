#ifndef _REG_ARR_NODE_H_
#define _REG_ARR_NODE_H_

#include <stdint.h>
#include <type_traits>
#include <array>
#include "halcpp_utils.h"

namespace halcpp{
// Credit for this solution goes to https://www.reddit.com/user/IyeOnline/

template<int32_t INDEX, uint32_t DIM>
constexpr uint32_t map_index()
{
    return INDEX == -1 ? DIM-1 : INDEX;
}

template<uint32_t STRIDE, std::size_t N>
constexpr uint32_t linear_index( std::array<uint32_t,N> nd_index, std::array<uint32_t,N> dimensions )
{
    uint32_t result = 0;
    uint32_t product = 1;
    for ( std::size_t i=0; i<N; ++i )
    {
        result += nd_index[N-i-1] * STRIDE * product;
        product *= dimensions[N-i-1];
    }

    return result;
}

constexpr bool valid_index( int32_t I, uint32_t E )
{
    return  I >= -1 and I < static_cast<int32_t>(E);
}

template<
    template<uint32_t B, uint32_t W, typename P> typename REG_T,
    uint32_t BASE, uint32_t WIDTH, uint32_t STRIDE, typename PARENT_TYPE, uint32_t ... Extents
>
class REG_ARR_NODE
{
    static constexpr uint32_t Dimensions = sizeof...(Extents);
    static_assert( Dimensions > 0 );

public :
    template<int32_t ... Indices>
    auto at()
    {
        static_assert( sizeof...(Indices) == Dimensions );
        static_assert( ( valid_index(Indices,Extents) && ... ) );
        constexpr uint32_t offset = BASE + linear_index<STRIDE>( std::array{ map_index<Indices,Extents>() ... }, std::array{ Extents ... } );

        return REG_T< offset, WIDTH, PARENT_TYPE >();
    }
};

}

#endif // !_REG_ARR_NODE_H_
