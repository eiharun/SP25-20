################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (12.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
S_SRCS += \
../Core/Startup/startup_stm32l412kbux.s 

OBJS += \
./Core/Startup/startup_stm32l412kbux.o 

S_DEPS += \
./Core/Startup/startup_stm32l412kbux.d 


# Each subdirectory must supply rules for building sources it contributes
Core/Startup/%.o: ../Core/Startup/%.s Core/Startup/subdir.mk
	arm-none-eabi-gcc -mcpu=cortex-m4 -g3 -DDEBUG -c -I"C:/Users/harun/OneDrive/Documents/School/VT/HAB/HAB_STM32/RFM95W_Rx/Drivers/RFM95W_HAL_Driver" -x assembler-with-cpp -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@" "$<"

clean: clean-Core-2f-Startup

clean-Core-2f-Startup:
	-$(RM) ./Core/Startup/startup_stm32l412kbux.d ./Core/Startup/startup_stm32l412kbux.o

.PHONY: clean-Core-2f-Startup

