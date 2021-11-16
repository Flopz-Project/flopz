
"""

$ flopz_listen.py --config flopz.json --link [UART|CAN] --output [CONSOLE, CHROME]


Events:
    - Trace
        - Function Trace *
        - BBLock Trace
    - InteractiveEvent
        - ShellEvent

main():
    link = get_link(args.link)
    config = parse_config(args.config)
    target = config.get_target()

    protocol = target.get_protocol()

    link.start()
    while True:
        data = link.get()
        protocol.feed(data)
        while protocol.has_event():
            event = protocol.get_event()
            if event.is_interactive():
                event.enter()
            else:
                logger.log(event)


class Protocol:
    def init:
        proto_state = INIT
        events = Queue()

    def feed(data):
        data_idx = 0
        while data_idx < len(data):
            if state = EXPECT_HEADER:
                # parse header:
                if data[data_idx] == 0x00:
                    state = EXPECT_FUNCTION_ID
                    data_idx += 1
                    continue
            if state == EXPECT_FUNCTION_ID:
                function_id = data[data_idx]
                # done, get back to EXPECT_HEADER
                events.push(FunctionTraceEvent(function_id))
                self.has_event = True
                state = EXPECT_HEADER
                data_idx = 0
                continue


"""