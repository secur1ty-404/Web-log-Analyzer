import re
from datetime import datetime
import pytz

class LogParser:
    def __init__(self):
        self.patterns = {
            'nginx_standard': re.compile(
                r'^(\S+)\s+-\s+-\s+\[([^\]]+)\]\s+"([A-Z]+)\s+([^\s"]+)\s+([^"]+)"\s+(\d+)\s+(\d+)\s+"([^"]*)"\s+"([^"]+)"'
            ),
            'nginx_custom': re.compile(
                r'^(\S+)\s+(\S+)\s+\[([^\]]+)\]\s+(\d+)\s+[\d.]+\s+\d+\s+(\S+)\s+(\S+)\s+(\S+):(\d+)\s+(\d+)\s+"([^"]*)"(?:\s+[\d.]+)?$'
            ),
            'apache': re.compile(
                r'^(\S+)\s+-\s+-\s+\[([^\]]+)\]\s+"(\S+)\s+(\S+)\s+\S+"\s+(\d+)\s+(\d+)'
            ),
            'iis': re.compile(
                r'^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)'
            )
        }
        
    def detect_format(self, sample_lines):
        """自动检测日志格式"""
        format_matches = {fmt: 0 for fmt in self.patterns.keys()}
        
        for line in sample_lines:
            for fmt, pattern in self.patterns.items():
                if pattern.match(line.strip()):
                    format_matches[fmt] += 1
                    
        # 返回匹配最多的格式
        return max(format_matches.items(), key=lambda x: x[1])[0]
        
    def parse_line(self, line):
        """解析单行日志"""
        line = line.strip()
        result = {}
        
        for fmt, pattern in self.patterns.items():
            match = pattern.match(line)
            if match:
                if fmt == 'nginx_standard':
                    result = {
                        'ip': match.group(1),
                        'timestamp': self._parse_timestamp(match.group(2)),
                        'method': match.group(3),
                        'url': match.group(4),
                        'protocol': match.group(5),
                        'status': match.group(6),
                        'body_bytes': match.group(7),
                        'referer': match.group(8) if match.group(8) else "-",
                        'user_agent': match.group(9)
                    }
                elif fmt == 'nginx_custom':
                    result = {
                        'ip': match.group(1),
                        'host': match.group(2),
                        'timestamp': self._parse_timestamp(match.group(3)),
                        'status': match.group(4),
                        'url': match.group(5),
                        'backend': f"{match.group(7)}:{match.group(8)}"
                    }
                elif fmt == 'apache':
                    result = {
                        'ip': match.group(1),
                        'timestamp': self._parse_timestamp(match.group(2)),
                        'method': match.group(3),
                        'url': match.group(4),
                        'status': match.group(5)
                    }
                elif fmt == 'iis':
                    result = {
                        'ip': match.group(1),
                        'timestamp': match.group(2),
                        'method': match.group(3),
                        'url': match.group(4),
                        'status': match.group(5)
                    }
                break
                
        return result
    def _parse_timestamp(self, timestamp_str):
        """解析时间戳"""
        try:
            dt = datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S %z")
            return dt.astimezone(pytz.utc)
        except:
            return None
    def summarize_ips(self):
        if not self.log_lines:
            messagebox.showwarning("警告", "请先上传日志文件")
            return

        # 使用集合自动去重
        unique_ips = set()
        
        for line in self.log_lines:
            parsed_log = self.log_parser.parse_line(line.strip())
            if parsed_log and parsed_log.get('ip'):
                unique_ips.add(parsed_log['ip'])
