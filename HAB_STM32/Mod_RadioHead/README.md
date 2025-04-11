# How to use

Just put both files in the RadioHead library directory (i.e. next to the RH_RF95.h file).

Then in your sketch, include the header file:

```cpp
#include <RH_RF95_CH.h>
```

From here you can use it just like the RH_RF95 class, but with the added functionality of custom headers.

The new functions are:

- setHeaders(seq,ack,cmd,len) -> void
- setHeaderSeq(seq) -> void
- setHeaderAck(ack) -> void
- setHeaderCMD(cmd) -> void
- setHeaderLen(len) -> void
- headerSeq() -> uint8_t
- headerAck() -> uint8_t
- headerCMD() -> uint8_t
- headerLen() -> uint8_t
- getHeaders(seq*,ack*,cmd*,len*) -> void

Including overwritten functions from `RHGenericDriver` class:

- setHeaderTo(to) -> void
- setHeaderFrom(from) -> void
- setHeaderId(id) -> void
- setHeaderFlags(set,clear) -> void[just use set]
- headerTo() -> uint8_t
- headerFrom() -> uint8_t
- headerId() -> uint8_t
- headerFlags() -> uint8_t

The overwritten functions have the same function as the new functions. And they correspond to each new header.

- To -> Seq
- From -> Ack
- Id -> CMD
- Flags -> Len

I would highly recommend using the new functions, as they help with readability and understanding of the code. The overwritten functions are there for backwards compatibility, but they are not recommended for use in this application.

Modified functions include

- send(data, len) -> bool
  - send is modified to include the new headers in the data packet rather than the old.
- validateRxBuf() -> void
  - validateRxBuf is modified to pass rxBuf validation. Previously validation would fail if header was set incorrectly. With the new application, the header being set correct is interpreted differently. So this implementation has changed. Previously it would pass if `_rxHeaderTo == _thisAddress || _rxHeaderTo == RH_BROADCAST_ADDRESS`. Now it will pass as long as the CMD part of the header is not 0. Previously if this function failed, the packet would be dropped. Therefore there was no need to change recv() function.
