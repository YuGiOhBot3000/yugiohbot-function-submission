variable "function_title" {
  description = "The name of the function."
  default     = "yugiohbot_submission"
}

variable "function_name" {
  description = "The name of the function archive."
  default     = "function"
}

variable "function_description" {
  description = "The description of the function."
  default     = "Submission handler for the YuGiOhBot Submission Site"
}

variable "function_runtime" {
  description = "The runtime for the function."
  default     = "python38"
}

variable "entry_point" {
  description = "The name of the function to run from main.py"
  default     = "function"
}