from transformers import TrainingArguments, Trainer
from transformers import DataCollatorForSeq2Seq
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from datasets import load_dataset,load_from_disk
from TextSummarizer.entity import ModelTrainerConfig
import torch


class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def train(self):
        CUDA_LAUNCH_BLOCKING="1"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tokenizer = AutoTokenizer.from_pretrained(self.config.model_ckpt)
        FalconSi = AutoModelForSeq2SeqLM.from_pretrained(self.config.model_ckpt)
        seq2seq_data_collator = DataCollatorForSeq2Seq(tokenizer,model=FalconSi)

        #loading_data
        dataset_samsum_pt = load_from_disk(self.config.data_path)

        trainer_args = TrainingArguments(
            output_dir=self.config.root_dir, num_train_epochs=self.config.num_train_epochs, warmup_steps=self.config.warmup_steps,
            per_device_train_batch_size=self.config.per_device_train_batch_size, per_device_eval_batch_size=self.config.per_device_train_batch_size,
            weight_decay=self.config.weight_decay, logging_steps=self.config.logging_steps,
            evaluation_strategy=self.config.evaluation_strategy, eval_steps=self.config.eval_steps, save_steps=1e6,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps
        )

        trainer = Trainer(model=FalconSi,args=trainer_args,tokenizer=tokenizer,
                          data_collator=seq2seq_data_collator,train_dataset=dataset_samsum_pt["test"],
                          eval_dataset=dataset_samsum_pt["validation"])
        
        trainer.train()

        #save_model
        FalconSi.save_model(os.path.join(self.config.root_dir,"pegasus-samsum-model"))
        #save_tokenizer
        tokenizer.save_pretrained(os.path.join(self.config.root_dir,"tokenizer"))
        
