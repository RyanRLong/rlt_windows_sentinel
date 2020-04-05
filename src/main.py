# -*- coding: utf-8 -*-
"""
.. module:: __main__
   :platform: Windows
   :synopsis: Main program execution

.. moduleauthor:: Ryan Long <ryalong1004@gmail.com>
"""
import asyncio

from models.command import Command


async def run():
    tasks = [
        Command("cleanmgr.exe /sagerun:1"),
        Command("wuauclt /detectnow /updatenow"),
        Command("cipher.exe /w:E"),
        Command("cipher.exe /w:C"),
        Command("sfc /scannow"),
    ]

    await asyncio.gather(*[task() for task in tasks])


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
