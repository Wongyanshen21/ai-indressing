export interface EditRequest {
  image: File;
  prompt: string;
  region: "clothing" | "hair" | "background";
}

export interface EditResponse {
  resultUrl: string;
  maskUrl: string;
}
