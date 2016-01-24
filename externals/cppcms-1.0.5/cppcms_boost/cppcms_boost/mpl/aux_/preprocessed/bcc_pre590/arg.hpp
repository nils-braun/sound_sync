
// Copyright Peter Dimov 2001-2002
// Copyright Aleksey Gurtovoy 2001-2004
//
// Distributed under the Boost Software License, Version 1.0. 
// (See accompanying file LICENSE_1_0.txt or copy at 
// http://www.boost.org/LICENSE_1_0.txt)
//

// *Preprocessed* version of the main "arg.hpp" header
// -- DO NOT modify by hand!

CPPCMS_BOOST_MPL_AUX_ADL_BARRIER_NAMESPACE_OPEN
template<> struct arg< -1 >
{
    CPPCMS_BOOST_STATIC_CONSTANT(int, value  = -1);
    CPPCMS_BOOST_MPL_AUX_ARG_TYPEDEF(na, tag)
    CPPCMS_BOOST_MPL_AUX_ARG_TYPEDEF(na, type)

    template<
          typename U1, typename U2, typename U3, typename U4, typename U5
        >
    struct apply
    {
        typedef U1 type;
        CPPCMS_BOOST_MPL_AUX_ASSERT_NOT_NA(type);
    };
};

template<> struct arg<1>
{
    CPPCMS_BOOST_STATIC_CONSTANT(int, value  = 1);
    typedef arg<2> next;
    CPPCMS_BOOST_MPL_AUX_ARG_TYPEDEF(na, tag)
    CPPCMS_BOOST_MPL_AUX_ARG_TYPEDEF(na, type)

    template<
          typename U1, typename U2, typename U3, typename U4, typename U5
        >
    struct apply
    {
        typedef U1 type;
        CPPCMS_BOOST_MPL_AUX_ASSERT_NOT_NA(type);
    };
};

template<> struct arg<2>
{
    CPPCMS_BOOST_STATIC_CONSTANT(int, value  = 2);
    typedef arg<3> next;
    CPPCMS_BOOST_MPL_AUX_ARG_TYPEDEF(na, tag)
    CPPCMS_BOOST_MPL_AUX_ARG_TYPEDEF(na, type)

    template<
          typename U1, typename U2, typename U3, typename U4, typename U5
        >
    struct apply
    {
        typedef U2 type;
        CPPCMS_BOOST_MPL_AUX_ASSERT_NOT_NA(type);
    };
};

template<> struct arg<3>
{
    CPPCMS_BOOST_STATIC_CONSTANT(int, value  = 3);
    typedef arg<4> next;
    CPPCMS_BOOST_MPL_AUX_ARG_TYPEDEF(na, tag)
    CPPCMS_BOOST_MPL_AUX_ARG_TYPEDEF(na, type)

    template<
          typename U1, typename U2, typename U3, typename U4, typename U5
        >
    struct apply
    {
        typedef U3 type;
        CPPCMS_BOOST_MPL_AUX_ASSERT_NOT_NA(type);
    };
};

template<> struct arg<4>
{
    CPPCMS_BOOST_STATIC_CONSTANT(int, value  = 4);
    typedef arg<5> next;
    CPPCMS_BOOST_MPL_AUX_ARG_TYPEDEF(na, tag)
    CPPCMS_BOOST_MPL_AUX_ARG_TYPEDEF(na, type)

    template<
          typename U1, typename U2, typename U3, typename U4, typename U5
        >
    struct apply
    {
        typedef U4 type;
        CPPCMS_BOOST_MPL_AUX_ASSERT_NOT_NA(type);
    };
};

template<> struct arg<5>
{
    CPPCMS_BOOST_STATIC_CONSTANT(int, value  = 5);
    typedef arg<6> next;
    CPPCMS_BOOST_MPL_AUX_ARG_TYPEDEF(na, tag)
    CPPCMS_BOOST_MPL_AUX_ARG_TYPEDEF(na, type)

    template<
          typename U1, typename U2, typename U3, typename U4, typename U5
        >
    struct apply
    {
        typedef U5 type;
        CPPCMS_BOOST_MPL_AUX_ASSERT_NOT_NA(type);
    };
};

CPPCMS_BOOST_MPL_AUX_NONTYPE_ARITY_SPEC(1,int, arg)

CPPCMS_BOOST_MPL_AUX_ADL_BARRIER_NAMESPACE_CLOSE
