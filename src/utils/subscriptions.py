import asyncio
import logging


def subscribe(generator, loop=None):
    def decorate(fn):
        return Subscription(generator, fn, loop=loop)
    return decorate


class Subscription:
    def __init__(self, generator, fn, loop=None):
        self._generator = generator
        self._fn = fn
        self._loop = loop if loop else asyncio.get_event_loop()
        self._task = None

    def start(self, _injected):
        if self._task is not None and not self._task.done():
            raise RuntimeError(
                'Task is already launched and is not completed.')

        self._task = asyncio.run_coroutine_threadsafe(
            self._run(_injected), self._loop)

    def stop(self):
        self._task.cancel()

    async def _run(self, _injected):
        while True:
            try:
                async for event in self._generator():
                    try:
                        await self._fn(_injected, event)
                    except Exception as e:
                        logging.error(e)
            except Exception as e:
                logging.error(e)
            logging.warning('Generator died, restarting')
