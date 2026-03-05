import { PatternMatch } from './types';

export interface DetectionRule {
  name: string;
  pattern: RegExp;
  description: string;
  severity: 'high' | 'medium' | 'low';
  category: 'malicious' | 'sensitive' | 'destructive' | 'network';
}

export const detectionRules: DetectionRule[] = [
  {
    name: 'base64 encoded payload',
    pattern: /eval\s*\(\s*atob\s*\(/i,
    description: '检测到 base64 解码后执行代码',
    severity: 'high',
    category: 'malicious'
  },
  {
    name: 'exec with dynamic code',
    pattern: /(eval|exec|Function)\s*\(\s*.*\+/i,
    description: '检测到动态代码执行',
    severity: 'high',
    category: 'malicious'
  },
  {
    name: 'obfuscated string',
    pattern: /fromCharCode.*join/i,
    description: '检测到字符串混淆',
    severity: 'medium',
    category: 'malicious'
  },
  {
    name: 'read SSH key',
    pattern: /(\.ssh\/id_rsa|\.ssh\/id_ed25519)/i,
    description: '检测到访问 SSH 密钥',
    severity: 'high',
    category: 'sensitive'
  },
  {
    name: 'read environment variables',
    pattern: /process\.env|os\.environ/i,
    description: '检测到读取环境变量',
    severity: 'medium',
    category: 'sensitive'
  },
  {
    name: 'send sensitive data',
    pattern: /(fetch|axios|http\.request).*(token|password|secret|key)/i,
    description: '检测到可能发送敏感数据',
    severity: 'high',
    category: 'sensitive'
  },
  {
    name: 'delete files',
    pattern: /(rmSync|unlink|rmdir).*\-rf/i,
    description: '检测到递归删除文件',
    severity: 'high',
    category: 'destructive'
  },
  {
    name: 'modify system config',
    pattern: /(echo|writeFile).*(\/etc\/|system32|registry)/i,
    description: '检测到修改系统配置',
    severity: 'high',
    category: 'destructive'
  },
  {
    name: 'reverse shell',
    pattern: /(bash|zsh).*\/dev\/tcp|netcat|nc\s+[\-e]/i,
    description: '检测到反弹 shell 特征',
    severity: 'high',
    category: 'network'
  },
  {
    name: 'external data exfiltration',
    pattern: /fetch\s*\(\s*['"]https?:\/\/(?!localhost|127\.0\.0\.1)/i,
    description: '检测到外发网络请求',
    severity: 'medium',
    category: 'network'
  }
];
