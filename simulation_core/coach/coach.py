class Coach:
    def __init__(self, internal_params):
        """
        초기화 함수.
        내부 파라미터를 받아 저장함.
        internal_params: dict
            시뮬레이션에서 생성된 정부, 기업, 대중 등의 파라미터 묶음
        """
        self.params = internal_params

    def adjust_weights(self):
        """
        내부 파라미터를 기반으로 뉴스, 대중, 기업, 정부 각각에 대한
        주가 반영 가중치를 계산하여 딕셔너리 형태로 반환.

        Returns:
            dict: {
                "w_news": float,
                "w_public": float,
                "w_company": float,
                "w_gov": float
            }
        """

        # 대중(public), 정부(government), 기업(company) 파라미터 분리
        p = self.params["public"]
        g = self.params["government"]
        c = self.params["company"]

        # 각 항목별 가중치 계산
        return {
            # 뉴스 가중치: 뉴스 민감도가 높을수록 영향력 증가 (기본값 0.4)
            "w_news": round(0.4 + 0.2 * p["news_sensitivity"], 3),

            # 대중 가중치: 리스크를 감수하려는 정도에 따라 조정 (기본값 0.3)
            "w_public": round(0.3 + 0.1 * p["risk_appetite"], 3),

            # 기업 가중치: R&D에 많이 투자하는 기업일수록 영향력 증가 (기본값 0.2)
            "w_company": round(0.2 + 0.2 * c["rnd_ratio"], 3),

            # 정부 가중치: 정책 방향성이 시장친화적일수록 영향력 증가 (기본값 0.1)
            "w_gov": round(0.1 + 0.2 * g["policy_direction"], 3) 
            
            #이후에 여러 파라미터 도입하여 확장(p, c, g)
        }