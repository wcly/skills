import { SecurityCheckResult, CheckOptions, StaticAnalysisResult, RepoReputationResult, OutputFormat } from './types';
import { parseInput, ParsedSource } from './inputParser';
import { cloneRepo } from './repoManager';
import { runStaticAnalysis } from './staticAnalyzer';
import { getRepoReputation } from './repoReputation';
import { generateReport } from './reporter';
import { monitorRuntime } from './runtimeMonitor';

export async function checkSecurity(options: CheckOptions): Promise<SecurityCheckResult> {
  const source = parseInput(options.input);
  const repoPath = await cloneRepo(source);
  
  const staticAnalysis = await runStaticAnalysis(repoPath);
  const reputation = await getRepoReputation(source);
  
  let runtimeBehavior = null;
  if (options.enableRuntimeCheck) {
    runtimeBehavior = await monitorRuntime(repoPath);
  }
  
  const result = calculateResult(staticAnalysis, reputation, runtimeBehavior);
  return result;
}

function calculateResult(
  staticAnalysis: StaticAnalysisResult,
  reputation: RepoReputationResult,
  runtimeBehavior?: any
): SecurityCheckResult {
  let score = 100;

  const highSeverity = 20;
  const mediumSeverity = 10;
  const lowSeverity = 5;

  for (const pattern of staticAnalysis.maliciousPatterns) {
    score -= pattern.severity === 'high' ? highSeverity : 
             pattern.severity === 'medium' ? mediumSeverity : lowSeverity;
  }

  for (const pattern of staticAnalysis.sensitiveDataAccess) {
    score -= pattern.severity === 'high' ? highSeverity : 
             pattern.severity === 'medium' ? mediumSeverity : lowSeverity;
  }

  for (const pattern of staticAnalysis.destructiveBehavior) {
    score -= pattern.severity === 'high' ? highSeverity : 
             pattern.severity === 'medium' ? mediumSeverity : lowSeverity;
  }

  for (const pattern of staticAnalysis.networkSuspicious) {
    score -= pattern.severity === 'high' ? highSeverity : 
             pattern.severity === 'medium' ? mediumSeverity : lowSeverity;
  }

  if (runtimeBehavior) {
    if (runtimeBehavior.dangerousScripts && runtimeBehavior.dangerousScripts.length > 0) {
      score -= runtimeBehavior.dangerousScripts.length * 15;
    }
    if (runtimeBehavior.suspiciousFileAccess && runtimeBehavior.suspiciousFileAccess.length > 0) {
      score -= runtimeBehavior.suspiciousFileAccess.length * 10;
    }
    if (runtimeBehavior.networkConnections && runtimeBehavior.networkConnections.length > 0) {
      score -= runtimeBehavior.networkConnections.length * 10;
    }
  }

  if (reputation.stars > 1000) score += 10;
  else if (reputation.stars > 100) score += 5;

  if (reputation.contributors > 10) score += 5;

  score = Math.max(0, Math.min(100, score));

  const riskLevel = score >= 70 ? 'low' : score >= 40 ? 'medium' : 'high';
  const recommendation = score >= 50 ? 'download' : 'not_recommended';

  const reasons: string[] = [];
  if (staticAnalysis.maliciousPatterns.length > 0) {
    reasons.push(`检测到 ${staticAnalysis.maliciousPatterns.length} 个恶意代码模式`);
  }
  if (staticAnalysis.sensitiveDataAccess.length > 0) {
    reasons.push(`检测到 ${staticAnalysis.sensitiveDataAccess.length} 个敏感数据访问`);
  }
  if (runtimeBehavior && runtimeBehavior.dangerousScripts && runtimeBehavior.dangerousScripts.length > 0) {
    reasons.push(`检测到 ${runtimeBehavior.dangerousScripts.length} 个危险脚本`);
  }
  if (reputation.stars < 10 && reputation.contributors < 3) {
    reasons.push('仓库缺乏足够的社会监督（stars 和贡献者较少）');
  }

  return {
    score,
    riskLevel,
    recommendation,
    reasons,
    details: {
      ...staticAnalysis,
      ...reputation,
      runtimeBehavior: runtimeBehavior || undefined
    }
  };
}

export { generateReport } from './reporter';
export { SecurityCheckResult, CheckOptions, OutputFormat } from './types';
