"""

Small POP server. Heavilly based on

pypopper: a file-based pop3 server (http://code.activestate.com/recipes/534131-pypopper-python-pop3-server/)

Useage:
    python server.py


    Will return all mail*.txt in the current folder as mail. Output is also printed.

"""
import logging
import socket
import glob

logging.basicConfig(format="%(message)s")
log = logging.getLogger("pypopper")
log.setLevel(logging.INFO)


class ChatterboxConnection(object):
    END = "\r\n"

    def __init__(self, conn):
        self.conn = conn

    def __getattr__(self, name):
        return getattr(self.conn, name)

    def sendall(self, data, END=END):
        if len(data) < 50:
            log.debug("send: %r", data)
        else:
            log.debug("send: %r...", data[:50])
        data += END
        self.conn.sendall(data)

    def recvall(self, END=END):
        data = []
        while True:
            chunk = self.conn.recv(4096)
            if END in chunk:
                data.append(chunk[:chunk.index(END)])
                break
            data.append(chunk)
            if len(data) > 1:
                pair = data[-2] + data[-1]
                if END in pair:
                    data[-2] = pair[:pair.index(END)]
                    data.pop()
                    break
        log.debug("recv: %r", "".join(data))
        return "".join(data)


class Message(object):
    def __init__(self, filename):
        global MSG_INDEX
        msg = open(filename, "r")
        try:
            self.data = data = msg.read()
            self.size = len(data)
            self.top, bot = data.split("\r\n\r\n", 1)
            self.bot = bot.split("\r\n")
            self.index = int(filename.split('mail')[1].split('.txt')[0])
        finally:
            msg.close()


def handleUser(data, msgs):
    log.info("USER:%s", data.split()[1])
    return "+OK user accepted"


def handlePass(data, msgs):
    log.info("PASS:%s", data.split()[1])
    return "+OK pass accepted"


def handleStat(data, msgs):
    return "+OK %i %i" % (len(msgs), sum([msg.size for msg in msgs]))


def handleList(data, msgs):
    return "+OK %i messages (%i octets)\r\n%s\r\n." % (len(msgs), sum([msg.size for msg in msgs]), '\r\n'.join(["%i %i" % (msg.index, msg.size,) for msg in msgs]))


def handleTop(data, msgs):
    cmd, num, lines = data.split()
    lines = int(lines)
    msg = msgs[int(num) - 1]
    text = msg.top + "\r\n\r\n" + "\r\n".join(msg.bot[:lines])
    return "+OK top of message follows\r\n%s\r\n." % text


def handleRetr(data, msgs):
    log.info("RETRIVE:%s", data.split()[1])
    msg = msgs[int(data.split()[1]) - 1]
    return "+OK %i octets\r\n%s\r\n." % (msg.size, msg.data)


def handleDele(data, msgs):
    log.info("DELETE:%s", data.split()[1])
    return "+OK message 1 deleted"


def handleNoop(data, msgs):
    return "+OK"


def handleQuit(data, msgs):
    return "+OK pypopper POP3 server signing off"

dispatch = dict(
    USER=handleUser,
    PASS=handlePass,
    STAT=handleStat,
    LIST=handleList,
    TOP=handleTop,
    RETR=handleRetr,
    DELE=handleDele,
    NOOP=handleNoop,
    QUIT=handleQuit,
)


def serve(host, port, filenames):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    try:
        if host:
            hostname = host
        else:
            hostname = "localhost"
        log.debug("pypopper POP3 serving '%s' on %s:%s", filenames, hostname, port)
        while True:
            sock.listen(1)
            conn, addr = sock.accept()
            log.debug('Connected by %s', addr)
            try:
                msgs = range(0, len(filenames))
                for f in filenames:
                    msg = Message(f)
                    msgs[msg.index-1] = msg
                conn = ChatterboxConnection(conn)
                conn.sendall("+OK pypopper file-based pop3 server ready")
                while True:
                    data = conn.recvall()
                    command = data.split(None, 1)[0]
                    try:
                        cmd = dispatch[command]
                    except KeyError:
                        conn.sendall("-ERR unknown command")
                    else:
                        conn.sendall(cmd(data, msgs))
                        if cmd is handleQuit:
                            return
            finally:
                conn.close()
                msgs = None
    except (SystemExit, KeyboardInterrupt):
        log.info("pypopper stopped")
    except Exception as ex:
        log.critical("fatal error", exc_info=ex)
    finally:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

if __name__ == "__main__":
    filenames = glob.glob("./mail[0-9]*.txt")

    serve("127.0.0.1", 22110, filenames)
