################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (12.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Drivers/RFM95W_HAL_Driver/lib/ideetron/AES-128_V10.c \
../Drivers/RFM95W_HAL_Driver/lib/ideetron/Encrypt_V31.c 

OBJS += \
./Drivers/RFM95W_HAL_Driver/lib/ideetron/AES-128_V10.o \
./Drivers/RFM95W_HAL_Driver/lib/ideetron/Encrypt_V31.o 

C_DEPS += \
./Drivers/RFM95W_HAL_Driver/lib/ideetron/AES-128_V10.d \
./Drivers/RFM95W_HAL_Driver/lib/ideetron/Encrypt_V31.d 


# Each subdirectory must supply rules for building sources it contributes
Drivers/RFM95W_HAL_Driver/lib/ideetron/%.o Drivers/RFM95W_HAL_Driver/lib/ideetron/%.su Drivers/RFM95W_HAL_Driver/lib/ideetron/%.cyclo: ../Drivers/RFM95W_HAL_Driver/lib/ideetron/%.c Drivers/RFM95W_HAL_Driver/lib/ideetron/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32L412xx -c -I../Core/Inc -I../Drivers/STM32L4xx_HAL_Driver/Inc -I../Drivers/STM32L4xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32L4xx/Include -I../Drivers/CMSIS/Include -I../Drivers/RFM95W_HAL_Driver -I../FATFS/Target -I../FATFS/App -I../Middlewares/Third_Party/FatFs/src -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-Drivers-2f-RFM95W_HAL_Driver-2f-lib-2f-ideetron

clean-Drivers-2f-RFM95W_HAL_Driver-2f-lib-2f-ideetron:
	-$(RM) ./Drivers/RFM95W_HAL_Driver/lib/ideetron/AES-128_V10.cyclo ./Drivers/RFM95W_HAL_Driver/lib/ideetron/AES-128_V10.d ./Drivers/RFM95W_HAL_Driver/lib/ideetron/AES-128_V10.o ./Drivers/RFM95W_HAL_Driver/lib/ideetron/AES-128_V10.su ./Drivers/RFM95W_HAL_Driver/lib/ideetron/Encrypt_V31.cyclo ./Drivers/RFM95W_HAL_Driver/lib/ideetron/Encrypt_V31.d ./Drivers/RFM95W_HAL_Driver/lib/ideetron/Encrypt_V31.o ./Drivers/RFM95W_HAL_Driver/lib/ideetron/Encrypt_V31.su

.PHONY: clean-Drivers-2f-RFM95W_HAL_Driver-2f-lib-2f-ideetron

