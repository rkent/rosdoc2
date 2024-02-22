
.. _program_listing_file_include_full_package_iamcpp.hpp:

Program Listing for File iamcpp.hpp
===================================

|exhale_lsh| :ref:`Return to documentation for file <file_include_full_package_iamcpp.hpp>` (``include/full_package/iamcpp.hpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   //
   //   Copyright 2022 R. Kent James <kent@caspia.com>
   //
   //   Licensed under the Apache License, Version 2.0 (the "License");
   //   you may not use this file except in compliance with the License.
   //   You may obtain a copy of the License at
   //
   //       http://www.apache.org/licenses/LICENSE-2.0
   //
   //   Unless required by applicable law or agreed to in writing, software
   //   distributed under the License is distributed on an "AS IS" BASIS,
   //   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   //   See the License for the specific language governing permissions and
   //   limitations under the License.
   
   #ifndef FULL_PACKAGE__IAMCPP_HPP_
   #define FULL_PACKAGE__IAMCPP_HPP_
   
   
   #include <tuple>
   #include "rclcpp/rclcpp.hpp"
   
   namespace full_package
   {
   
   class DoSomeCpp: public rclcpp::node
   {
   public:
     DoSomeCpp();
     virtual ~DoSomeCpp() {}
   
     static std::tuple<double, double> apply_powers(
       const double_t number,  
       const double exponent   
     );
   
   
     size_t count
   };
   
   }  // namespace full_package
   
   #endif  // FULL_PACKAGE__IAMCPP_HPP_
