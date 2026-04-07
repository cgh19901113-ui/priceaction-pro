"""
GitHub 仓库质量评估工具 - 简化版

使用 GitHub REST API，无需 gh CLI 认证
基于 github-quality skill 的评分体系简化实现
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class GitHubRepoEvaluator:
    def __init__(self, token: Optional[str] = None):
        self.session = requests.Session()
        if token:
            self.session.headers['Authorization'] = f'token {token}'
        self.session.headers['Accept'] = 'application/vnd.github.v3+json'
    
    def fetch_repo_data(self, owner: str, repo: str) -> Dict:
        """获取仓库基础数据"""
        url = f'https://api.github.com/repos/{owner}/{repo}'
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return {}
    
    def fetch_commits(self, owner: str, repo: str, days: int = 180) -> List:
        """获取最近 N 天的 commits"""
        since = (datetime.now() - timedelta(days=days)).isoformat() + 'Z'
        url = f'https://api.github.com/repos/{owner}/{repo}/commits'
        params = {'since': since, 'per_page': 100}
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return []
    
    def fetch_releases(self, owner: str, repo: str) -> List:
        """获取 Releases"""
        url = f'https://api.github.com/repos/{owner}/{repo}/releases'
        params = {'per_page': 20}
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return []
    
    def fetch_issues(self, owner: str, repo: str, state: str = 'all') -> Dict:
        """获取 Issues 统计"""
        url = f'https://api.github.com/repos/{owner}/{repo}/issues'
        params = {'state': state, 'per_page': 1}
        response = self.session.get(url, params=params)
        
        # 从 Link header 获取总数
        total = 0
        if 'Link' in response.headers:
            links = response.headers['Link'].split(',')
            for link in links:
                if 'rel="last"' in link:
                    # 提取 page 参数
                    url_part = link.split(';')[0].strip()
                    page_param = url_part.split('page=')[1].split('>')[0]
                    total = int(page_param)
                    break
        
        return {'total': total, 'sample': response.json() if response.status_code == 200 else []}
    
    def calculate_score(self, owner: str, repo: str, repo_data: Dict, commits: List, releases: List, issues: Dict) -> Dict:
        """计算三层评分"""
        
        # ========== Layer 1: 客观指标 (40%) ==========
        layer1_score = 0
        layer1_details = {}
        
        # 1. Star 增长效率 (7%)
        stars = repo_data.get('stargazers_count', 0)
        created_at = datetime.strptime(repo_data['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        months_old = max(1, (datetime.now() - created_at).days / 30)
        stars_per_month = stars / months_old
        
        if stars_per_month > 1000:
            star_score = 100
        elif stars_per_month > 200:
            star_score = 90
        elif stars_per_month > 50:
            star_score = 75
        elif stars_per_month > 10:
            star_score = 60
        elif stars_per_month > 1:
            star_score = 40
        else:
            star_score = 20
        
        # 年轻项目折扣
        if months_old < 6:
            star_score *= 0.8
        
        layer1_details['star_growth'] = f"{stars_per_month:.1f} stars/month → {star_score}/100"
        layer1_score += star_score * 0.07
        
        # 2. Fork/Star 比率 (9%)
        forks = repo_data.get('forks_count', 0)
        fork_ratio = forks / stars if stars > 0 else 0
        
        if 0.08 <= fork_ratio <= 0.30:
            fork_score = 100
        elif 0.05 <= fork_ratio < 0.08 or 0.30 < fork_ratio <= 0.60:
            fork_score = 85
        elif 0.03 <= fork_ratio < 0.05:
            fork_score = 65
        elif fork_ratio < 0.03:
            fork_score = 40
        else:
            fork_score = 30
        
        layer1_details['fork_star_ratio'] = f"{fork_ratio:.2f} → {fork_score}/100"
        layer1_score += fork_score * 0.09
        
        # 3. Commit 活跃度 (10%)
        commits_180d = len(commits)
        
        if commits_180d >= 100:
            commit_score = 80
        elif commits_180d >= 50:
            commit_score = 65
        elif commits_180d >= 20:
            commit_score = 50
        elif commits_180d >= 10:
            commit_score = 40
        elif commits_180d >= 5:
            commit_score = 35
        else:
            commit_score = 20
        
        layer1_details['commit_activity'] = f"{commits_180d} commits/180d → {commit_score}/100"
        layer1_score += commit_score * 0.10
        
        # 4. Release 频率 (7%)
        releases_12m = len([r for r in releases if datetime.strptime(r['published_at'], '%Y-%m-%dT%H:%M:%SZ') > datetime.now() - timedelta(days=365)])
        
        if releases_12m >= 6:
            release_score = 100
        elif releases_12m >= 3:
            release_score = 80
        elif releases_12m >= 1:
            release_score = 60
        elif commits_180d > 0:
            release_score = 40
        else:
            release_score = 20
        
        layer1_details['release_frequency'] = f"{releases_12m} releases/12m → {release_score}/100"
        layer1_score += release_score * 0.07
        
        # 5. 时间衰减
        last_commit = commits[0]['commit']['committer']['date'] if commits else repo_data['updated_at']
        last_commit_dt = datetime.strptime(last_commit, '%Y-%m-%dT%H:%M:%SZ')
        days_since = (datetime.now() - last_commit_dt).days
        decay = max(0.60, 2.718 ** (-days_since / 365))
        
        layer1_details['time_decay'] = f"Last commit {days_since} days ago → decay={decay:.2f}"
        layer1_score *= decay
        
        # ========== Layer 2: 工程质量 (40%) ==========
        layer2_score = 0
        layer2_details = {}
        
        # 1. README 质量 (11%)
        readme_score = 0
        if repo_data.get('has_readme', True):  # GitHub 默认都有
            readme_url = f'https://raw.githubusercontent.com/{owner}/{repo}/main/README.md'
            alt_urls = [
                f'https://raw.githubusercontent.com/{owner}/{repo}/master/README.md',
                f'https://raw.githubusercontent.com/{owner}/{repo}/main/README.rst',
                f'https://raw.githubusercontent.com/{owner}/{repo}/master/README.rst',
            ]
            
            for url in [readme_url] + alt_urls:
                resp = self.session.get(url)
                if resp.status_code == 200:
                    readme_content = resp.text
                    # 简单评估：长度 + 是否有截图/示例
                    if len(readme_content) > 1000:
                        readme_score += 40
                    if '![ ' in readme_content or '<img' in readme_content:
                        readme_score += 30
                    if '```' in readme_content:
                        readme_score += 30
                    break
        
        layer2_details['readme_quality'] = f"{readme_score}/100"
        layer2_score += readme_score * 0.11
        
        # 2. 目录结构 (10%) - 简化：检查是否有标准目录
        dir_score = 50  # 默认中等
        if repo_data.get('size', 0) > 1000:  # >1MB
            dir_score = 70
        if repo_data.get('language') in ['Python', 'JavaScript', 'TypeScript']:
            dir_score += 10
        
        layer2_details['directory_structure'] = f"{dir_score}/100"
        layer2_score += dir_score * 0.10
        
        # 3. CI/CD 配置 (9%) - 检查是否有 workflow 文件
        ci_score = 0
        ci_url = f'https://api.github.com/repos/{owner}/{repo}/contents/.github/workflows'
        ci_resp = self.session.get(ci_url)
        if ci_resp.status_code == 200:
            workflows = ci_resp.json()
            if isinstance(workflows, list) and len(workflows) > 0:
                ci_score = min(100, 60 + len(workflows) * 10)
        
        layer2_details['ci_cd'] = f"{ci_score}/100"
        layer2_score += ci_score * 0.09
        
        # 4. 安全配置 (4%)
        security_score = 0
        for sec_file in ['SECURITY.md', '.github/SECURITY.md', '.github/dependabot.yml']:
            url = f'https://api.github.com/repos/{owner}/{repo}/contents/{sec_file}'
            if self.session.get(url).status_code == 200:
                security_score += 50
        security_score = min(100, security_score)
        
        layer2_details['security'] = f"{security_score}/100"
        layer2_score += security_score * 0.04
        
        # 5. Commit message 质量 (6%) - 简化：检查长度
        msg_score = 50
        if commits:
            recent_msgs = [c['commit']['message'].split('\n')[0] for c in commits[:10]]
            avg_len = sum(len(m) for m in recent_msgs) / len(recent_msgs)
            if avg_len > 50:
                msg_score = 80
            elif avg_len > 30:
                msg_score = 60
        
        layer2_details['commit_message'] = f"{msg_score}/100"
        layer2_score += msg_score * 0.06
        
        # ========== Layer 3: 社区口碑 (20%) ==========
        layer3_score = 0
        layer3_details = {}
        
        # 1. Issue 讨论质量 (12%) - 简化：只看开启/关闭比
        issue_score = 50
        close_rate = 0
        open_issues = repo_data.get('open_issues_count', 0)
        closed_issues = issues.get('total', 0) - open_issues
        if issues.get('total', 0) > 0:
            close_rate = closed_issues / issues['total']
            if close_rate > 0.8:
                issue_score = 100
            elif close_rate > 0.6:
                issue_score = 80
            elif close_rate > 0.4:
                issue_score = 60
            elif close_rate > 0.2:
                issue_score = 40
        
        layer3_details['issue_quality'] = f"Close rate {close_rate*100:.1f}% → {issue_score}/100"
        layer3_score += issue_score * 0.12
        
        # 2. Twitter/X 讨论 (8%) - 跳过，用基准分
        twitter_score = 55  # 基线
        layer3_details['twitter'] = f"{twitter_score}/100 (baseline, no xreach)"
        layer3_score += twitter_score * 0.08
        
        # ========== 最终评分 ==========
        final_score = layer1_score + layer2_score + layer3_score
        
        # 生命周期分类
        if days_since < 30:
            lifecycle = "Active Development"
        elif days_since < 180:
            lifecycle = "Mature/Stable"
        elif days_since < 365:
            lifecycle = "Maintenance Mode"
        else:
            lifecycle = "Stable/Complete"
        
        if repo_data.get('archived'):
            lifecycle = "Archived"
        
        return {
            'final_score': round(final_score, 1),
            'layer1': round(layer1_score / 0.4, 1),
            'layer2': round(layer2_score / 0.4, 1),
            'layer3': round(layer3_score / 0.2, 1),
            'lifecycle': lifecycle,
            'details': {
                'layer1': layer1_details,
                'layer2': layer2_details,
                'layer3': layer3_details
            }
        }
    
    def evaluate(self, repo_url: str) -> Dict:
        """评估一个 GitHub 仓库"""
        # 解析 URL
        if 'github.com' not in repo_url:
            return {'error': 'Invalid GitHub URL'}
        
        parts = repo_url.rstrip('/').split('/')
        if len(parts) < 5:
            return {'error': 'Invalid URL format'}
        
        owner = parts[-2]
        repo = parts[-1]
        
        print(f"\n评估：{owner}/{repo}")
        print("-" * 50)
        
        # 获取数据
        repo_data = self.fetch_repo_data(owner, repo)
        if not repo_data:
            return {'error': 'Repo not found or private'}
        
        commits = self.fetch_commits(owner, repo)
        releases = self.fetch_releases(owner, repo)
        issues = self.fetch_issues(owner, repo)
        
        # 计算评分
        result = self.calculate_score(owner, repo, repo_data, commits, releases, issues)
        
        # 补充信息
        result['repo'] = {
            'name': f"{owner}/{repo}",
            'description': repo_data.get('description', ''),
            'stars': repo_data.get('stargazers_count', 0),
            'forks': repo_data.get('forks_count', 0),
            'language': repo_data.get('language', ''),
            'created': repo_data['created_at'][:10],
            'updated': repo_data['updated_at'][:10]
        }
        
        return result


def print_report(result: Dict):
    """打印评估报告"""
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    repo = result['repo']
    
    print(f"\n{'='*60}")
    print(f"GitHub Repo Quality Report")
    print(f"{'='*60}")
    print(f"\nFinal Score: {result['final_score']}/100")
    
    # 评级
    if result['final_score'] >= 85:
        rating = "High Quality"
    elif result['final_score'] >= 70:
        rating = "Good Quality"
    elif result['final_score'] >= 55:
        rating = "Average Quality"
    else:
        rating = "Weak Quality"
    
    print(f"Rating: {rating}")
    print(f"Lifecycle: {result['lifecycle']}")
    print(f"\nRepo: {repo['name']}")
    print(f"Description: {repo['description']}")
    print(f"Stars: {repo['stars']} | Forks: {repo['forks']}")
    print(f"Language: {repo['language']}")
    print(f"Created: {repo['created']} | Updated: {repo['updated']}")
    
    print(f"\n{'-'*60}")
    print(f"Layer Scores")
    print(f"{'-'*60}")
    print(f"Layer 1 (Objective):     {result['layer1']}/100 (weight 40%)")
    print(f"Layer 2 (Engineering):   {result['layer2']}/100 (weight 40%)")
    print(f"Layer 3 (Community):     {result['layer3']}/100 (weight 20%)")
    
    print(f"\n{'-'*60}")
    print(f"Details")
    print(f"{'-'*60}")
    
    for layer, details in result['details'].items():
        print(f"\n{layer.upper()}:")
        for metric, value in details.items():
            print(f"  - {metric}: {value}")
    
    print(f"\n{'='*60}")


def main():
    # 要评估的仓库列表
    repos_to_eval = [
        # 一人公司/SaaS
        "https://github.com/easychen/one-person-businesses-methodology",
        "https://github.com/wasp-lang/open-saas",
        "https://github.com/nextjs/saas-starter",
        "https://github.com/TryGhost/Ghost",
        "https://github.com/FujiwaraChoki/MoneyPrinterV2",
        
        # 量化交易
        "https://github.com/vnpy/vnpy",
        "https://github.com/microsoft/qlib",
        "https://github.com/freqtrade/freqtrade",
        "https://github.com/nautechsystems/nautilus_trader",
        "https://github.com/ccxt/ccxt",
        
        # AI/自动化
        "https://github.com/harry0703/MoneyPrinterTurbo",
        "https://github.com/linyqh/NarratoAI",
        "https://github.com/Huanshere/VideoLingo",
        "https://github.com/virattt/ai-hedge-fund",
        "https://github.com/virattt/dexter",
        
        # 数据工具
        "https://github.com/ranaroussi/yfinance",
        "https://github.com/mrjbq7/ta-lib",
        "https://github.com/twopirllc/pandas-ta",
    ]
    
    evaluator = GitHubRepoEvaluator()
    
    print("\n" + "="*60)
    print("GitHub Repo Batch Evaluation")
    print("="*60)
    
    results = []
    for repo_url in repos_to_eval:
        result = evaluator.evaluate(repo_url)
        print_report(result)
        results.append(result)
    
    # 汇总排名
    print("\n" + "="*60)
    print("Top 10 Ranking")
    print("="*60)
    
    valid_results = [r for r in results if 'error' not in r]
    sorted_results = sorted(valid_results, key=lambda x: x['final_score'], reverse=True)
    
    for i, r in enumerate(sorted_results[:10], 1):
        print(f"{i}. {r['repo']['name']}: {r['final_score']}分 - {r['lifecycle']}")


if __name__ == "__main__":
    main()
