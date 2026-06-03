from models.report_export import ReportExport
from repositories.base import BaseRepository


class ReportExportRepository(BaseRepository):
    def __init__(self):
        super().__init__(ReportExport)

    def get_by_analysis_id(self, analysis_id):
        return self.model.query.filter_by(analysis_id=analysis_id).all()
