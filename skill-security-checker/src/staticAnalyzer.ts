import * as fs from 'fs';
import * as path from 'path';
import { glob } from 'glob';
import { StaticAnalysisResult, PatternMatch } from './types';
import { detectionRules } from './detectionPatterns';

export async function runStaticAnalysis(repoPath: string): Promise<StaticAnalysisResult> {
  const files = await glob('**/*.{js,ts,py,sh,rb}', { cwd: repoPath, nodir: true });
  
  const result: StaticAnalysisResult = {
    maliciousPatterns: [],
    sensitiveDataAccess: [],
    destructiveBehavior: [],
    networkSuspicious: []
  };

  for (const file of files) {
    const filePath = path.join(repoPath, file);
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');

    lines.forEach((line, index) => {
      for (const rule of detectionRules) {
        if (rule.pattern.test(line)) {
          const match: PatternMatch = {
            file,
            line: index + 1,
            code: line.trim().substring(0, 100),
            description: rule.name,
            severity: rule.severity
          };

          switch (rule.category) {
            case 'malicious':
              result.maliciousPatterns.push(match);
              break;
            case 'sensitive':
              result.sensitiveDataAccess.push(match);
              break;
            case 'destructive':
              result.destructiveBehavior.push(match);
              break;
            case 'network':
              result.networkSuspicious.push(match);
              break;
          }
        }
      }
    });
  }

  return result;
}
