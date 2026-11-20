import { MayabotiClient } from "@/lib/mayaboti-client";
import type { InboundEvent } from "@/lib/types";

export function createStreamClient(onSend: (frame: string) => void = () => {}) {
  const socket = {
    readyState: 1,
    onopen: null as (() => void) | null,
    onmessage: null as ((event: MessageEvent) => void) | null,
    send: onSend,
    close() {},
  };
  const client = new MayabotiClient({
    url: "ws://test", reconnect: false,
    socketFactory: () => socket as unknown as WebSocket,
  });
  client.connect();
  socket.onopen?.();
  return {
    client,
    socket,
    receive(event: InboundEvent) {
      socket.onmessage?.({ data: JSON.stringify(event) } as MessageEvent);
    },
  };
}
